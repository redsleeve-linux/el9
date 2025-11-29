-- patch-git, a patch management tooling for dist-git.
-- Copyright Red Hat, Inc.
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

--[==[
The canonical source for this file is here:

* https://gitlab.com/redhat/centos-stream/rpms/glibc/-/blob/c10s/patch-git.lua

To activate patch-git, add this file into your dist-git repository, and
add this line to the spec file:

%{lua:dofile(rpm.expand([[%_sourcedir/patch-git.lua]]))}

Do not indent this line, and use this line verbatim.  Some tools
may use it to recognize that patch-git is in use.

If patch-git can infer the patch list correctly, you can remove all
Patch…: lines from the spec file, and replace them with a line
like this:

%{lua:patchgit.patches()}

If the patch-git heuristics do not result in a correct patch
application order (which can happen if sorting patches
lexicographically within one commit does not yield the correct patch
application order), you can keep historic Patch…: lines before the
patchgit.patches() line.

To auto-generate the changelog, start the %changelog section like this:

%changelog
%{lua:patchgit.changelog()}

This will add auto-generated changelog entries from the Git history.
]==]

-- The patchgit global variable caches data extracted from Git-generated files,
-- and provides functions that can be called from the spec file.
--
-- patchgit.commits: a list which contains the commit history.  The
--   oldest commit is at index 1, its successor is at index 2,
--   and so on.  The table entries are themselves tables with the
--   following fields:
--     commit: Git commit hash (40 hexadecimal digits)
--     author: name and email address of the commit author
--     author_date: author date according to Git
--     committer: like author, but for the Git committer
--     commit_date: like author_date, but for the commit
--     message: the commit message (unparsed)
--     changes: the file changes (from git log --raw output).  A list
--       of tables with the following fields:
--         src_mode: number with file mode, 0 for creation
--         dst_mode: number with file mode, 0 for deletion
--         src_blob: abbreviated blob hash for original
--         dst_blob: abbreviated blob hash for result
--         status:   flags, should only be 'A' (add), 'M' (modify),
--                   'D' (delete) (due to --no-renames)
--         path:     path of the blob being changed
--
-- patchgit.patches(): Emit a patch list constructed from Git history
--   into the spec file.
--
-- patchgit.changelog(): Emit auto-generated changelog entries into the
--   spec file.
--
patchgit = {}

-- Used to trigger file regeneration in case of changes.  This is only
-- necessary to change if the set of files or the data format in the
-- files is changed.  If data extraction from the files is modified,
-- this change will take place immediately even if those files are not
-- regenerated, so no VERSION update is needed.
local VERSION = 1

-- Cached value of %_sourcedir from the RPM environment.  When not
-- running under rpm, default to the current directory.
local sourcedir
if rpm then
   sourcedir = rpm.expand('%_sourcedir')
else
   -- If not running under rpm, default to the current directory.
   sourcedir = '.'
end

-- This file contains the commit hash for HEAD (corresponding to the
-- rest of the files) and the VERSION marker.
local git_commit_file = 'patch-git-generated-commit.txt'

-- This file contains git log --raw output.
local git_log_file = 'patch-git-generated-log.txt'

-- Read the file with the specified name in the RPM source directory.
-- Returns nil and an error message if the source file cannot be opened.
local function read_source_file(name)
   local path = sourcedir .. '/' .. name
   local fp, err = io.open(path, 'r')
   if not fp then
      return fp, err
   end
   local s = fp:read('a')
   assert(fp:close())
   return s
end

-- Write the specified contents to a file with the specified name in
-- the RPM source directory.  Asserts if the file cannot be written.
local function write_source_file(name, contents)
   local fp = assert(io.open(sourcedir .. '/' .. name, 'w+'))
   assert(fp:write(contents))
   assert(fp:close())
end

-- Run 'git ' .. cmd in the RPM source directory and return the output
-- string.  Assert that the command completed successfully.
local function run_git(cmd)
   cmd = 'cd ' .. sourcedir .. ' && TZ=UTC LC_ALL=C.utf8 git ' .. cmd
   local fp = assert(io.popen(cmd, 'r'))
   local s = fp:read('a')
   local ok, term, status = fp:close()
   if not ok or term ~= 'exit' or status ~= 0 then
      assert(false, cmd .. ': ' .. term .. ' ' .. status)
   end
   return s
end

-- Check the result of os.execute and the close method on streams
-- created by io.popen.  The first argument is the command to use in
-- an error message.
local function check_cmd_result(cmd, ok, term, status)
   if not ok or term ~= 'exit' or status ~= 0 then
      assert(false, cmd .. ': ' .. term .. ' ' .. status)
   end
end

-- Run the command with the shell and return the output.
local function run_shell(cmd)
   local fp = assert(io.popen(cmd, 'r'))
   local s = fp:read('a')
   check_cmd_result(cmd, fp:close())
   return s
end

-- Calls f with a temporary file name as an argument, which is created
-- automatically.  Delete the file once f returns (normally or through
-- an error).
local function with_temporary_file(f, ...)
   local tmpfile = assert(string.match(run_shell('mktemp'), '^(/.*)\n$'))
   local fp = assert(io.open(tmpfile, 'w+'))
   return (function(ok, ...)
         os.remove(tmpfile)
         if ok then
            return ...
         else
            error(...)
         end
   end)(pcall(f, tmpfile, ...))
end

-- Run 'git ' .. cmd in the RPM source directory and assert that the
-- command completed successfully.
local function check_git(cmd)
   cmd = 'cd ' .. sourcedir .. ' && TZ=UTC LC_ALL=C.utf8 git ' .. cmd
   check_cmd_result(cmd, os.execute(cmd))
end

-- Lists the contents of the directory.  The special entries '.' and
-- '..'  are included.
local function list_directory(path)
   if posix then
      return posix.dir(path)
   else
      -- Not running under rpm.  Avoid additional dependencies
      -- by falling back to ls.  Not ideal, but gets the job done
      -- (unless there are files with newlines in their names).
      local result = {}
      local cmd = 'ls -a -- ' .. path
      local fp = assert(io.popen(cmd, 'r'))
      while true do
         local line = fp:read('l')
         if not line then
            break
         end
         result[#result + 1] = line
      end
      check_cmd_result(cmd, fp:close())
      return result
   end
end

-- Return the single RPM spec file name from the source directory.
local function get_single_spec_file()
   local spec
   for _, file in ipairs(list_directory(sourcedir)) do
      if string.match(file, '%.spec$') then
         if spec then
            error('multiple RPM spec files: '
                  .. spec .. ' and ' .. file)
         end
         spec = file
         break
      end
   end
   if not spec then
      error('RPM spec file not found')
   end
   return spec
end

-- Quote a string so that shell meta-characters are not interpreted by
-- the shell anymore.
local function shell_quote(s)
   if s == '' then
      return "''"
   end
   if not string.match(s, '[^A-Za-z0-9_./+-]') then
      -- The string does not contain shell meta-characters.
      return s
   end
   -- Replace "'" with a sequence that ends the string, emits an escaped
   -- "'", and then starts a new string.
   return "'" .. string.gsub(s, "'", [['\'']]) .. "'"
end
-- Tests for shell_quote.
do
   assert(shell_quote('') == "''")
   assert(shell_quote('foo') == 'foo')
   assert(shell_quote('foo bar') == "'foo bar'")
   assert(shell_quote("foo'bar") == "'foo'\\''bar'")
   assert(shell_quote("'foo'bar") == "''\\''foo'\\''bar'")
end

local function shell_args(args)
   local result = {}
   for _, arg in ipairs(args) do
      result[#result + 1] = shell_quote(arg)
   end
   return table.concat(result, ' ')
end
-- Tests for shell_args.
do
   assert(shell_args({}) == '')
   assert(shell_args({'foo', 'bar'}) == "foo bar")
   assert(shell_args({'foo', "bar'baz"}) == [[foo 'bar'\''baz']])
end

-- Evaluate the string using rpmspec against the spec file
-- (previously obtained with get_single_spec_file).  Return the result
-- of the evaluation.  The mode of operation needs to be selected with
-- rpmspec options such as --eval, --qf, -P.
local run_rpmspec
-- Same as check_rpmspec, but print the result to stdout.
local check_rpmspec
do
   local function cmd(spec, ...)
      return shell_args({'rpmspec', '-D', '_sourcedir ' .. sourcedir,
                         sourcedir .. '/' .. spec, ...})
   end

   function run_rpmspec(spec, ...)
      local script = cmd(spec, ...)
      local fp = assert(io.popen(script, 'r'))
      local result = assert(fp:read('a'))
      check_cmd_result(script, fp:close())
      return result
   end

   function check_rpmspec(spec, ...)
      local script = cmd(spec, ...)
      check_cmd_result(script, os.execute(script))
   end
end

-- Testing helper: assert_eq(a, b) asserts if not a == b.
-- A third argument can be provided with a context string.
local assert_eq
do
   -- quote(v) returns a string that evaluates to v, mostly in Lua syntax.
   local quote
   do
      local quote_table = {
         ['\n'] = '\\n',
         ['\r'] = '\\r',
         ['\t'] = '\\t',
         ['\0'] = '\000',
         ['"'] = '\\"',
         ['\\'] = '\\\\',
      }
      local function quote_table_update(i)
         local ch = string.char(i)
         if quote_table[ch] == nil then
            quote_table[ch] = string.format('\\x%02x', i)
         end
      end
      for i=0,31 do
         quote_table_update(i)
      end
      for i=127,255 do
         quote_table_update(i)
      end
      local function quote1(v, seen)
	 if v == nil then
	    return 'nil'
	 elseif v == true then
	    return 'true'
	 elseif v == false then
	    return 'false'
	 elseif type(v) == 'number' then
	    return string.format('%q', v)
	 elseif type(v) == 'string' then
	    return '"' .. string.gsub(v, '.', quote_table) .. '"'
	 elseif type(v) == 'table' then
	    -- Prevent infinite recursion.
	    local idx = seen[v]
	    if idx then
	       return '&' .. idx
	    end
	    local seen_count = seen[1] + 1
	    seen[1] = seen_count
	    seen[v] = seen_count

	    local count = 0
	    for _, _ in pairs(v) do
	       count = count + 1
	    end
	    local result = {}
	    if count == #v then
	       -- Regular table.
	       for i=1,count do
		  result[i] = quote1(v[i], seen)
	       end
	    else
	       -- Not a regular table.
	       for key, value in pairs(v) do
		  result[#result + 1] =
		     '[' .. quote1(key, seen) .. ']='
		     .. quote1(value, seen)
	       end
	    end
	    return '{' .. table.concat(result, ', ') .. '}'
	 else
	    return '#<' .. type(v) .. ':' .. quote(tostring(v)) .. '>'
	 end
      end
      function quote(v)
	 return quote1(v, {0})
      end
   end
   assert(quote('') == '""')
   assert(quote('\n') == '"\\n"')
   assert(quote('{}') == '"{}"')
   assert(quote({}) == '{}')
   assert(quote({1, 2, 3}) == '{1, 2, 3}')
   assert(quote({a=1}) == '{["a"]=1}')

   local deep_eq
   do
      local function deep_eq1(a, b, seen)
	 if a == b then
	    return true
	 elseif type(a) == 'table' and type(b) == 'table' then
	    assert(not seen[a])
	    assert(not seen[b])
	    seen[a] = true
	    seen[b] = true
	    local acount = 0
	    for ak, av in pairs(a) do
	       if not deep_eq1(av, b[ak], seen) then
		  return false
	       end
	       acount = acount + 1
	    end
	    local bcount = 0
	    for bk, bv in pairs(b) do
	       bcount = bcount + 1
	    end
	    return acount == bcount
	 else
	    return false
	 end
      end
      function deep_eq(a, b)
	 if a == b then
	    return true
	 elseif type(a) == 'table' and type(b) == 'table' then
	    return deep_eq1(a, b, {})
	 end
      end
   end

   function assert_eq(a, b, ctx)
      if deep_eq(a, b) then
	 return
      end
      local prefix
      if ctx then
	 prefix = ctx .. ': '
      else
	 prefix = ''
      end
      assert(a == b, prefix .. quote(a) .. ' ~= ' .. quote(b))
   end
end

-- Sort the list lexicographically, in place, treating sequences of
-- digits as a single positive decimal number.
local function version_sort(list)
   -- Sorting is only needed for two or more elements.
   if #list <= 1 then
      return
   end

   -- Maximum length of a sequence of consecutive digits in patch names.
   local max_width = 1
   for i=1,#list do
      local s = list[i]
      for number in string.gmatch(s, '%d+') do
         if #number > max_width then
            max_width = #number
         end
      end
   end

   -- Pad the number argument with leading '0' to max_width.
   local function pad(s)
      return string.rep('0', max_width - #s) .. s
   end

   local padded = {}
   for i=1,#list do
      local s = list[i]
      padded[s] = string.gsub(s, '%d+', pad)
   end

   table.sort(list, function (a, b)
                 return padded[a] < padded[b]
   end)
end
-- Tests for version_sort.
do
   local test = {'b2-30b', 'b1', 'b10', 'b2', 'a', 'b2-30', 'b2-4'}
   version_sort(test)
   assert(#test == 7)
   assert(test[1] == 'a')
   assert(test[2] == 'b1')
   assert(test[3] == 'b2')
   assert(test[4] == 'b2-4')
   assert(test[5] == 'b2-30')
   assert(test[6] == 'b2-30b')
   assert(test[7] == 'b10')
end

-- Returns true if the git command version is at least that of the
-- argument string.
local check_git_version
do
   -- Cached version of the git command.
   local git_version

   function check_git_version(reference)
      if not git_version then
	 local output = run_git('version')
	 git_version = assert(
	    string.match(output, '^git version (%d[^\n]*)\n'), output)
      end
      -- If the reference version sorts first, the version check succeeds.
      local sorted = {git_version, reference}
      version_sort(sorted)
      return sorted[1] == reference
   end
end

-- Called to generate the files (if HEAD or the script version has changed).
local function generate_files()
   -- True if %_sourcedir refers to a Git repository and git is installed.
   local have_git = (posix == nil -- Not running under rpm.
                     or (posix.access('/usr/bin/git', 'x')
                         and posix.access(sourcedir .. '/.git/.', 'x')))
   local commit_marker_contents -- For git_commit_file.
   if have_git then
      commit_marker_contents =
         run_git('rev-parse HEAD') .. 'v' .. VERSION .. '\n'
      if commit_marker_contents == read_source_file(git_commit_file) then
         -- HEAD and version did not change.  No file generation
         return
      end
   elseif not read_source_file(git_commit_file) then
      assert(false, 'no Git repository and no captured Git history')
   else
      -- No Git, so no regeneration possible, but the required files
      -- are present.  No work to do.
      return
   end

   -- At this point, we have a Git repository, and we need to regenerate the
   -- patch-git-generated*.txt files.  Make sure that the repository is not
   -- shallow.
   do
      local shallow = run_git('rev-parse --is-shallow-repository')
      if shallow == 'true\n' then
	 if check_git_version('2.28') then
	    check_git('fetch --unshallow --filter=blob:none')
	 else
	    -- 2.27 and earlier error out if the original clone did not
	    -- use --filter.
	    check_git('fetch --unshallow')
	 end
      else
         assert(shallow == 'false\n', shallow)
      end
   end

   -- Delete the marker file if it exists, to force regeneration after
   -- partial generation below.
   os.remove(sourcedir .. '/' .. git_commit_file)

   -- Produce the Git log.  The --first-parent option ignores side
   -- branches (so that it is possible to merge in arbitrary history
   -- without growing the log too much, and to control the
   -- script-processed commit messages).  With --no-renames, no blobs
   -- are needed (see --filter=blob:none above).  With --raw,
   -- information about the changed files is preserved (required for
   -- patch depth sorting below).  To include committer dates, use
   -- --pretty=fuller.
   check_git(
      'log --first-parent --no-renames --raw --pretty=fuller --date=default > '
      .. git_log_file)

   -- Atomically replace the contents of git_commit_file, confirming that
   -- the new Git log has been written.
   write_source_file(git_commit_file .. '.tmp', commit_marker_contents)
   assert(os.rename(sourcedir .. '/' .. git_commit_file .. '.tmp',
                    sourcedir .. '/' .. git_commit_file))
end

-- Older RPM versions use doubles for patch and source numbers, not
-- integers.  This causes problems because current Lua formats such
-- numbers with a decimal point.  Therefore, use tointeger when
-- obtaining numbers from source_nums, patch_nums.  If the Lua
-- interpreter has the double/integer distinction, it defines
-- math.tointeger.  Otherwise, the conversion is not necessary, and
-- doubles that are formatted without a decimal point if there are
-- integers.
local tointeger = math.tointeger
if not tointeger then
   function tointeger(n)
      return n
   end
end

-- Inject Sources: lines for the auto-generated files and this script
-- into the spec file.
local function emit_sources()
   -- If not running under rpm, the source list is not meaningful.  Do
   -- not print it.
   if not rpm then
      return
   end

   local max = 0
   for i=1,#source_nums do
      local k = source_nums[i]
      if k > max then
         max = tointeger(k)
      end
   end
   local function emit(name)
      max = max + 1
      print('Source' .. max .. ': ' .. name .. '\n')
   end
   emit(git_commit_file)
   emit(git_log_file)
   emit('patch-git.lua') -- This file.
end

local function parse_commits()
   local fp = assert(io.open(sourcedir .. '/' .. git_log_file), 'r')
   local line -- The current line.  Updated by readline1(), readline().
   local lineno = 0 -- Its number.
   local function readline1() -- No error checking, may return nil.
      lineno = lineno + 1
      line = fp:read('L') -- Include '\n'.
      return line
   end
   local function readline() -- Does not return nil.
      if not readline1() then
         assert(false, 'unexpected end of file at line ' .. lineno)
      end
      return line
   end
   local function check(cond) -- Report an error if not cond.
      if not cond then
         io.stderr:write(git_log_file .. ':' .. lineno .. ': error: '
                         .. line)
         io.stderr:write(debug.traceback(nil, 2))
         error('git log parse error')
      end
   end

   local commits = {}
   readline()

   while line do
      local commit = string.match(line, '^commit ([0-9-a-f]+)\n')
      check(commit and #commit == 40)
      if string.match(readline(), '^Merge: ') then
         readline()
      end
      local author = string.match(line, '^Author:    (.+)\n')
      check(author)
      local author_date = string.match(readline(), '^AuthorDate: (.+)\n')
      check(author_date)
      local committer = string.match(readline(), '^Commit:    (.+)\n')
      check(committer)
      local commit_date = string.match(readline(), '^CommitDate: (.+)\n')
      check(commit_date)
      check(readline() == '\n') -- Separator between header and commit message.

      -- Read the commit message.  Remove the indentation.
      local remove_indent = '^    (.*\n)'
      local message = {string.match(readline(), remove_indent)}
      check(message[1])
      while true do
         if not readline1() then
            -- EOF in initial commit message.
            break
         end
         local l = string.match(line, remove_indent)
         if not l then break
            -- No longer the commit message.
            break
         end
         message[#message + 1] = l
      end
      message = table.concat(message)

      if line == '\n' then
         readline1()
      end

      -- Read the file changes (lines starting with ':').
      local changes = {}
      while line and string.match(line, '^:') do
         local src_mode, dst_mode, src_blob, dst_blob, status, path =
            string.match(
               line,
               '^:([0-7]+) ([0-7]+) ([0-9a-f]+) ([0-9a-f]+) ([^\t]+)\t([^\n]+)\n')
         check(string.match(status, '^[ADM]$')) -- See patchgit.patches below.
         check(path)
         changes[#changes + 1] = {
            src_mode=tonumber(src_mode, 8),
            dst_mode=tonumber(dst_mode, 8),
            src_blob=src_blob,
            dst_blob=dst_blob,
            status=status,
            path=path,
         };
         readline1()
      end

      -- Store the commit.
      commits[#commits + 1] = {
         commit=commit,
         author=author,
         author_date=author_date,
         committer=committer,
         commit_date=commit_date,
         message=message,
         changes=changes,
      }

      if line == '\n' then
         readline1()
      end
   end
   assert(fp:close())

   -- Reverse the order of the commits list, so that the oldest commit
   -- comes first.
   do
      local i = 1
      local j = #commits
      while i < j do
         local tmp = commits[i]
         commits[i] = commits[j]
         commits[j] = tmp
         i = i + 1
         j = j - 1
      end
   end

   patchgit.commits = commits
end

-- Inject the Patch: lines into the spec file, in the appropriate
-- (commit) order.  Unapplied patches found in the source directory
-- and that are not present in the Git history are applied last.
function patchgit.patches(options)
   local history_only = options and options.history_only
   emit_sources()

   -- Maximum patch number emitted so far.
   local patchno = 0

   -- True entries for patch files that have already been applied in
   -- the spec file.  Only populated when running under rpm.
   local preordered = {}

      -- Table with the patches in the source directory.  As patches are
   -- scheduled for application, they are removed from this table.
   local patches_in_sourcedir = {}

   if not history_only then
      for i=1,#patches do
         -- Remove the %_sourcedir prefix.
         local pname = assert(string.match(patches[i], '.*/([^/]+)$'))
         preordered[pname] = true
         local n = patch_nums[i]
         if n > patchno then
            patchno = tointeger(n)
         end

      end
      for _, fname in ipairs(list_directory(sourcedir)) do
         if string.find(fname, '%.patch$') and not preordered[fname] then
            patches_in_sourcedir[fname] = true
         end
      end
   end

   -- Table indexed by patch name, mapping it to the age (number) of
   -- the patch.  Lower age numbers are applied earlier.
   local patch_age = {}
   for age, commit in ipairs(patchgit.commits) do
      for _, change in ipairs(commit.changes) do
         -- Only look at patch files in the top-level directory.
         if string.match(change.path, '^[^/]+%.patch$') then
            if change.status == 'A' then -- Add.
               assert(not patch_age[change.path], change.path)
               patch_age[change.path] = age
            elseif change.status == 'D' then -- Delete.
               assert(patch_age[change.path], change.path)
               patch_age[change.path] = nil
            elseif change.status == 'M' then -- Modify.
               assert(patch_age[change.path], change.path)
            else
               assert(false) -- See [ADM] match above.
            end
         end
      end
   end

   -- If not running under rpm, the default Lua print function behaves
   -- differently (it adds a '\n').  Directly write to stdout to avoid
   -- adding the extra '\n'.
   local emit
   if rpm then
      emit = print
   else
      function emit(s)
         io.stdout:write(s)
      end
   end


   -- Group the patches by age.  The keys of by_age are the age numbers.
   -- The values are lists of patch names (initially unsorted).
   local by_age = {}
   local max_age = #patchgit.commits
   for patch, age in pairs(patch_age) do
      assert(age <= max_age)
      local patchlist = by_age[age]
      if not patchlist then
         patchlist = {}
         by_age[age] = patchlist
      end
      patchlist[#patchlist + 1] = patch
   end

   -- Perform version sort on the table and emit the patch names in
   -- that order.
   local function emit_patchlist(patchlist)
      -- Within one commit, patches are sorted lexicographically.
      -- Remove the '.patch' suffix, so that it does not interfere
      -- with sorting ('patch2b.patch' sorting before 'patch2.patch').
      local list = {}
      for i, name in ipairs(patchlist) do
         list[i] = assert(string.match(name, '^(.+)%.patch$'))
      end
      version_sort(list)
      for i=1,#list do
         local pname = list[i] .. '.patch'
         if not preordered[pname] then
            patchno = patchno + 1
            emit('Patch' .. patchno .. ': ' .. pname .. '\n')
            patches_in_sourcedir[pname] = nil
         end
      end
   end

   -- Do not use ipairs here because the by_age table may have holes.
   -- Iterate over the maximum possible age range instead.
   for age=1,max_age do
      local patchlist = by_age[age]
      if patchlist then
         emit_patchlist(patchlist)
      end
   end

   -- Emit the unapplied patches in the source directory.
   if not history_only then
      local remaining_patches = {}
      for patch, _ in pairs(patches_in_sourcedir) do
         remaining_patches[#remaining_patches + 1] = patch
      end
      emit_patchlist(remaining_patches)
   end
end

----------------------------------------------------------------------
-- Processing of commit messages, for release numbers and changelogs
----------------------------------------------------------------------

-- Return a table with the issue numbers in the string.
-- Return nil if the argument is not valid or empty.
-- If previous is not nil, the tickets are appended to this list.
local function parse_ticket_string(tag, s, previous)
   local result
   if previous ~= nil then
      result = previous
   else
      result = {}
   end
   local old = #result
   for ref1 in string.gmatch(s, '[ \t\n]*([^ \t\n]+)[ \t\n]*') do
      local ref = string.match(ref1, '([a-zA-Z0-9#-]+),?')
      if not ref then
         return nil, 'invalid ticket reference: ' .. ref1
      end
      if not string.match(ref, '.*%d$') then
         return nil, 'ticket reference without trailing number: ' .. ref
      end
      for i=1,#result do
         if result[i] == ref1 then
            return nil, 'duplicate ticket reference: ' .. ref
         end
      end
      result[#result + 1] = ref
   end
   if #result == old then
      return nil, 'no ticket references found in ' .. tag
   end
   return result
end
-- Tests for parse_ticket_string.
do
   local t, err
   t = assert(parse_ticket_string('Resolves', ' RHEL-1234 swbz#567\n'))
   assert(#t == 2)
   assert(t[1] == 'RHEL-1234')
   assert(t[2] == 'swbz#567')
   t = assert(parse_ticket_string('Resolves', ' RHEL-1234, swbz#567\n'))
   assert(#t == 2)
   assert(t[1] == 'RHEL-1234')
   assert(t[2] == 'swbz#567')
   t, err = parse_ticket_string('Related', ' ')
   assert(not t)
   assert(err == 'no ticket references found in Related')
   t, err = parse_ticket_string('Related', ' bug 567')
   assert(not t)
   assert(err == 'ticket reference without trailing number: bug')
end

-- Append a line to the changelog table.  It is prefixed with '- '.
-- Long lines are wrapped at word boundaries and indented.
local function append_to_rpm_changelog(line, result)
   if #result == 0 then
      result[1] = '-'
   end
   for word in string.gmatch(line, '%S+') do
      if #result[#result] + #word > 76 then
	 result[#result + 1] = '  ' .. word
      else
	 result[#result] = result[#result] .. ' ' .. word
      end
   end
end


-- Extract the trailers from the passed commit message. Returns a
-- single table where keys are derived from the trailer tags.
-- On error, returns nil and an error message.
--
-- The result table may contain the following fields:
--
--   tickets: list of ticket reference strings (Resolves:, Related:)
--   parent: Git commit hash, 40 characters (Parent:)
--   patchgit_version: numeric revision number for patch-git directives.
--   rpm_branch_type: 'zstream' if present (RPM-Branch-Type:)
--   rpm_skip_release: boolean; true to skip release increment (RPM-Skip-Release:)
--   rpm_changelog: table of changelog entry strings
--   rpm_changelog_stop: boolean; true to stop including older commits
--     (RPM-Changelog-Stop:)
--   rpm_release: RPM release string (RPM-Release:)
--   rpm_version: RPM version string (RPM-Version:)
--
-- The rpm_changelog table contains zero or more strings, each of
-- which is a changelog entry.  The leading '-' is not included.
local parse_trailer
do
   -- Parser for Patch-Git-Version.
   local function parse_patchgit_version(tag, s)
      s = string.match(s, '%s*(%d+)%s*$')
      local n = s and tonumber(s)
      if not s or s ~= tostring(n) then
         return nil, tag .. ' does not contain a number'
      end
      return n
   end
   -- Tests for parse_patchgit_version.
   do
      local n, err
      assert(parse_patchgit_version('Patch-Git-Version', ' 0\n') == 0)
      assert(parse_patchgit_version('Patch-Git-Version', ' 1\n') == 1)
      assert(parse_patchgit_version('Patch-Git-Version', ' 2\n') == 2)
      n, err = parse_patchgit_version('Patch-Git-Version', '')
      assert(not n and err == 'Patch-Git-Version does not contain a number')
      n, err = parse_patchgit_version('Patch-Git-Version', ' \n')
      assert(not n and err == 'Patch-Git-Version does not contain a number')
      n, err = parse_patchgit_version('Patch-Git-Version',
				      ' 9999999999999999999\n')
      assert(not n and err == 'Patch-Git-Version does not contain a number')
   end

   -- Validator for RPM-Changelog.  It returns the changelog entries
   -- as a table of lines.  The lines start with '- ' or '  ', unless
   -- they are empty.
   local function parse_rpm_changelog(tag, s)
      assert(string.sub(s, #s) == '\n')

      -- '-' is used to denote no changelog entry.
      if string.match(s, '%s*%-%s*$') then
         return {}
      end

      local lines = {}
      for line in string.gmatch(s, '([^\n]+)\n') do
         lines[#lines + 1] = line
      end
      -- Remove leading whitespace from the first line.
      lines[1] = assert(string.match(lines[1], '^[ \t]*(.*)$'))
      if #lines == 1 then
         -- Nothing to do
      else
         -- Strip shared whitespace prefix from second and further lines.
         -- First compute the shared prefix.
         local prefix = assert(string.match(lines[2], '^([ \t]+)'))
         for i=3,#lines do
            -- Reduce the shared prefix length until equality is reached.
            while prefix ~= '' and string.sub(lines[i], 1, #prefix) ~= prefix do
               prefix = string.sub(prefix, 1, #prefix - 1)
            end
         end
         local skip = #prefix + 1
         -- Then strip the shared prefix.
         for i=2,#lines do
            lines[i] = string.sub(lines[i], skip)
         end
      end

      local result = {}
      if not string.match(lines[1], '^- ') then
         -- This is not an itemized changelog entry.  Concatenate all
         -- lines with word-wrapping.
         for _, line in ipairs(lines) do
	    append_to_rpm_changelog(line, result)
	 end
      else
	 local dashed = false
	 for lineno, line in ipairs(lines) do
	    if lineno > 1 and string.match(line, '^- ') then
	       dashed = true
	    end
	 end

	 for lineno, line in ipairs(lines) do
	    if not string.match(line, '^- ') then
	       if string.match(line, '^%s*$') then
		  line = ''
	       elseif not dashed then
		  -- If there are no '- ' lines in the continuation
		  -- part, all lines need to be indented to line up
		  -- with with the '- ' from the first line.
		  line = '  ' .. line
	       end
	    end
            result[lineno] = line
         end
      end
      return result
   end
   -- Tests for parse_rpm_changelog.
   do
      local function prc(s)
         return parse_rpm_changelog('RPM-Changelog', s)
      end

      -- Single-line changelog entry, not itemized.
      assert_eq(assert(prc('Switch to patch-git\n')),
		{'- Switch to patch-git'})

      -- Single-line changelog entry, itemized.
      assert_eq(assert(prc(' - Switch to patch-git\n')),
		{'- Switch to patch-git'})

      -- Multi-line changelog entry, not itemized.
      assert_eq(assert(prc(' Switch to\n  patch-git\n')),
		{'- Switch to patch-git'})

      -- Multi-line changelog entry, one item.
      assert_eq(assert(prc('- Switch to\n  patch-git\n')),
		{'- Switch to', '  patch-git'})

      -- Multi-line changelog entry, two items.
      assert_eq(assert(prc([[- Switch to
  patch-git
 - Additional patch-git
    fixes
]])),
		{'- Switch to',
		 ' patch-git',
		 '- Additional patch-git',
		 '   fixes'})
   end

   local function parse_rpm_release(tag, s)
      s = string.match(s, '^%s(%g+)%s*$')
      if not s then
         return nil, tag .. ' must contain a single word'
      end
      local dist = string.find(s, '%{?dist}', 1, true)
      if not dist then
         return nil, tag .. ' must contain %{?dist}'
      end
      if string.find(s, '%%.*%%{%?dist}')
         or string.find(s, '%%{%?dist}.*%%') then
         return nil, tag .. ' contains unexpected RPM macros'
      end
      if string.find(s, '-', 1, true) then
         return nil, tag .. ' contains "-"'
      end
      if not string.find(s, '%d') then
         return nil, tag .. ' must contain a digit'
      end
      return s
   end
   -- Tests for parse_rpm_release.
   do
      local r, err
      assert(parse_rpm_release('RPM-Release', ' 59%{?dist}\n') == '59%{?dist}')
      r, err = parse_rpm_release('RPM-Release', ' 59.el10\n')
      assert(not r)
      assert(err == 'RPM-Release must contain %{?dist}')
      r, err = parse_rpm_release('RPM-Release', ' 59.el10_0\n')
      assert(not r)
      assert(err == 'RPM-Release must contain %{?dist}')
      r, err = parse_rpm_release('RPM-Release', ' %{?dist}\n')
      assert(not r)
      assert(err == 'RPM-Release must contain a digit')
      r, err = parse_rpm_release('RPM-Release', '59 %{?dist}')
      assert(not r)
      assert(err == 'RPM-Release must contain a single word')
   end

   local function parse_parent(tag, s)
      local commit = string.match(s, '^%s*([0-9a-f]+)%s*\n')
      if not commit then
	 return nil, 'commit hash expected in ' .. tag
      elseif #commit ~= 40 then
	 return nil, 'full 40-character commit hash needed in ' .. tag
      end
      return commit
   end
   do
      local r, err
      assert(assert(parse_parent('Parent',
		' 92dfd986b2f2c697144be2ebe10a27d72c660ba4\n'))
	     == '92dfd986b2f2c697144be2ebe10a27d72c660ba4')
      r, err = parse_parent('Parent',
			    ' 92dfd986b2f2c697144be2ebe10a27d72c660ba4.\n')
      assert(not r)
      assert(err == 'commit hash expected in Parent')
      r, err = parse_parent('Parent',
			    ' 92dfd986b2f2c697144be2ebe10a27d72c660ba\n')
      assert(not r)
      assert(err == 'full 40-character commit hash needed in Parent')
   end

   local function parse_rpm_version(tag, s)
      s = string.match(s, '^%s(%g+)%s*$')
      if not s then
         return nil, tag .. ' must contain a single word'
      end
      if string.find(s, '%', 1, true) then
         return nil, tag .. ' contains unexpected RPM macros'
      end
      if string.find(s, '-', 1, true) then
         return nil, tag .. ' contains "-"'
      end
      if not string.find(s, '%d') then
         return nil, tag .. ' must contain a digit'
      end
      return s
   end
   -- Tests for parse_rpm_version.
   do
      local v, err
      assert(parse_rpm_version('RPM-Version', ' 2.39.1\n') == '2.39.1')
      v, err = parse_rpm_version('RPM-Version', ' 1%{?dist}\n')
      assert(not v)
      assert(err == 'RPM-Version contains unexpected RPM macros')
      v, err = parse_rpm_version('RPM-Version', ' %{version}\n')
      assert(not v)
      assert(err == 'RPM-Version contains unexpected RPM macros')
      v, err = parse_rpm_version('RPM-Version', ' 2-39\n')
      assert(not v)
      assert(err == 'RPM-Version contains "-"')
      v, err = parse_rpm_version('RPM-Version', ' version\n')
      assert(not v)
      assert(err == 'RPM-Version must contain a digit')
      v, err = parse_rpm_version('RPM-Version', ' 2 39\n')
      assert(not v)
      assert(err == 'RPM-Version must contain a single word')
   end

   local string_to_bool = {
      yes=true,
      no=false,
      ['true']=true,
      ['false']=false,
      ['0']=false,
      ['1']=true,
   }
   local function parse_bool(tag, s)
      s = string.match(s, '^%s*([^%s]+)%s*$')
      local flag
      if s ~= nil then
         flag = string_to_bool[s]
      end
      if flag == nil then
         return nil, tag .. ' must be yes/no'
      end
      return flag
   end
   -- Tests for parse_bool.
   do
      local bad = {'', 'y', 'n', '0 0', '0 1', 'none', 'Yes', 'No', 't', 'f'}
      local function ps(pfx, sfx)
	 assert(parse_bool('Bool', pfx .. 'yes' .. sfx) == true)
	 assert(parse_bool('Bool', pfx .. 'no' .. sfx) == false)
	 assert(parse_bool('Bool', pfx .. 'true' .. sfx) == true)
	 assert(parse_bool('Bool', pfx .. 'false' .. sfx) == false)
	 assert(parse_bool('Bool', pfx .. '0' .. sfx) == false)
	 assert(parse_bool('Bool', pfx .. '1' .. sfx) == true)
	 for _, value in ipairs(bad) do
	    local r, err = parse_bool('Bool', pfx .. value .. sfx)
	    assert(not r, value)
	    assert(err == 'Bool must be yes/no')
	 end
      end
      ps('', '')
      ps(' ', '\n')
      ps('  ', ' \n')
   end

   local function parse_rpm_branch_type(tag, s)
      s = string.match(s, '^%s*([^%s]+)%s*$')
      if s ~= 'zstream' then
         return nil, tag .. ' must be zstream'
      end
      return s
   end
   -- Tests for parse_rpm_branch_type.
   do
      assert(parse_rpm_branch_type('Branch', ' zstream\n') == 'zstream')
      local b, err = parse_rpm_branch_type('Branch', ' \n')
      assert(not b and err == 'Branch must be zstream')
      local b, err = parse_rpm_branch_type('Branch', ' hotfix\n')
      assert(not b and err == 'Branch must be zstream')
   end

   -- These are the recognized trailer tags in Git commit messages.
   -- (Git calls them keys, see git-interpret-trailers(1).)
   local recognized_trailer_tags = {
      ['Resolves']={field='tickets',
                    parse=parse_ticket_string,
                    duplicates=true},
      ['Parent']={parse=parse_parent},
      ['Patch-Git-Version']={parse=parse_patchgit_version,
                             need_parent=true,
                             field='patchgit_version'},
      ['RPM-Branch-Type']={parse=parse_rpm_branch_type},
      ['RPM-Skip-Release']={parse=parse_bool},
      ['RPM-Changelog']={parse=parse_rpm_changelog},
      ['RPM-Changelog-Stop']={parse=parse_bool,
                              need_parent=true},
      ['RPM-Release']={parse=parse_rpm_release,
                       need_parent=true},
      ['RPM-Version']={parse=parse_rpm_version,
                       need_parent=true},
   }
   recognized_trailer_tags.Related = recognized_trailer_tags.Resolves
   for k, v in pairs(recognized_trailer_tags) do
      if not v.field then
         v.field = string.lower(string.gsub(k, '%-', '_'))
      end
   end

   function parse_trailer(message)
      -- This holds due to the format of the input file.
      assert(string.sub(message, #message) == '\n')

      -- Skip the non-trailer part in the message.  There is no reverse
      -- find, so call string.find repeatedly, under the assumption that
      -- it's simpler and faster than the alternatives.
      local pos = 0
      do
         while true do
            -- Only skip one '\n', in case there are more than two.
            local npos = string.find(message, '\n\n', pos + 1, true)
            if not npos then
               if pos == 0 then
                  -- No '\n\n', no trailer.
                  return nil, 'missing Git trailer'
               end
               pos = pos + 2
               break
            end
            pos = npos
         end
      end

      -- pos is the start of the next line to parse.
      local result = {}
      local tags_seen = {} -- Keys are tag names, not fields. Values are true.
      local last_tag
      local need_parent -- Name of tag that requires Parent:.
      while true do
         local tag, contents, npos =
            string.match(message, '^([%w-]+):([^\n]*\n)()', pos)
         if not npos then
            if pos > #message then
               break
            elseif not last_tag then
               -- Probably just a new paragraph in the commit message.
               return nil, 'no Git trailer found'
            else
               return nil, 'malformed line in Git trailer after ' .. last_tag
                  .. ' tag'
            end
         end
         pos = npos
         last_tag = tag

         -- Find the tag descriptor.
         local descr = recognized_trailer_tags[tag]
         if not descr then
            return nil, 'not a recognized Git trailer tag: ' .. tag
         end
         if descr.need_parent then
            need_parent = tag
         end

         if tags_seen[tag] and not descr.duplicates then
            return nil, 'duplicate ' .. tag .. ' tag'
         end
         tags_seen[tag] = true

         -- Append indented continuation lines.
         while true do
            local cont, npos = string.match(message, '^([ \t][^\n]*\n)()', pos)
            if not cont then
               break
            end
            pos = npos
            -- This has quadratic behavior.  Assume that there are few
            -- continuation lines.
            contents = contents .. cont
         end

         local value, err = descr.parse(tag, contents, result[descr.field])
         if value == nil then
            return nil, err
         end
         result[descr.field] = value
      end
      if not last_tag then
         return nil, 'no Git trailer found'
      end
      if need_parent and not result.parent then
         return nil, need_parent .. ' requires Parent tag'
      end
      return result
   end
   -- Tests for parse_trailer.
   do
      local t, err
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

- Backport: Remove memory leak in fdopen (bug 31840)
- Backport: libio: Test for fdopen memory leak without SEEK_END
  support (bug 31840)

Resolves: RHEL-108475
]])
      assert(t, err)
      assert(t.tickets)
      assert(#t.tickets == 1)
      assert(t.tickets[1] == 'RHEL-108475')
      assert(t.patchgit_version == nil)
      assert(t.rpm_version == nil)
      assert(t.rpm_release == nil)
      assert(t.rpm_changelog_stop == nil)
      assert(t.rpm_branch_type == nil)

      -- Initial commit.
      t, err = parse_trailer([[Switch to patch-git

Resolves: RHEL-111490
Parent: 92dfd986b2f2c697144be2ebe10a27d72c660ba4
Patch-Git-Version: 1
RPM-Version: 2.39
RPM-Release: 60%{?dist}
RPM-Changelog-Stop: yes
]])
      assert(t, err)
      assert(t.tickets)
      assert(#t.tickets == 1)
      assert(t.tickets[1] == 'RHEL-111490')
      assert(t.patchgit_version == 1)
      assert(t.rpm_version == '2.39')
      assert(t.rpm_release == '60%{?dist}')
      assert(t.rpm_changelog_stop == true)
      assert(t.rpm_branch_type == nil)

      -- Missing blank line before Resolves:.
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

- Backport: Remove memory leak in fdopen (bug 31840)
- Backport: libio: Test for fdopen memory leak without SEEK_END
  support (bug 31840)
Resolves: RHEL-108475
]])
      assert(not t)
      assert(err == 'no Git trailer found', err)

      -- RPM release is set.
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

Resolves: RHEL-108475
Parent: 46a31fdf250a30ae96c082376a8eab95252762c0
RPM-Release: 59%{?dist}
]])
      assert(t, err)
      assert(t.parent == '46a31fdf250a30ae96c082376a8eab95252762c0')
      assert(t.rpm_release == '59%{?dist}')

      -- RPM-Version requires Parent and accepts a simple version.
      t, err = parse_trailer([[Set version for next release

Resolves: RHEL-108475
RPM-Version: 2.39.1
]])
      assert(not t)
      assert(err == 'RPM-Version requires Parent tag')

      t, err = parse_trailer([[Set version for next release

Resolves: RHEL-108475
Parent: 46a31fdf250a30ae96c082376a8eab95252762c0
RPM-Version: 2.39.1
]])
      assert(t, err)
      assert(t.rpm_version == '2.39.1')

      -- Duplicate RPM-Release:.
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

Resolves: RHEL-108475
RPM-Release: 59%{?dist}
RPM-Release: 59%{?dist}.1
]])
      assert(not t)
      assert(err == 'duplicate RPM-Release tag', err)

      -- Duplicate RPM-Version:.
      t, err = parse_trailer([[Set version for next release

Resolves: RHEL-108475
Parent: 46a31fdf250a30ae96c082376a8eab95252762c0
RPM-Version: 2.39.1
RPM-Version: 2.39.2
]])
      assert(not t)
      assert(err == 'duplicate RPM-Version tag', err)

      -- Multiple trailers.
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

- Backport: Remove memory leak in fdopen (bug 31840)
- Backport: libio: Test for fdopen memory leak without SEEK_END
  support (bug 31840)

Resolves: RHEL-108475
Resolves: swbz#31840
RPM-Skip-Release: yes
]])
      assert(t, err)
      assert(#t.tickets, 2)
      assert(t.tickets[1] == 'RHEL-108475')
      assert(t.tickets[2] == 'swbz#31840')
      assert(not t.rpm_release)
      assert(t.rpm_skip_release == true)

      -- Invalid value for Resolves trailer.
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

- Backport: Remove memory leak in fdopen (bug 31840)
- Backport: libio: Test for fdopen memory leak without SEEK_END
  support (bug 31840)

Resolves: RHEL-108475
Related:
RPM-Release: no
]])
      assert(not t)
      assert(err == 'no ticket references found in Related')

      -- Broken line in trailer.
      t, err = parse_trailer([[Fix memory leak after fdopen seek failure

- Backport: Remove memory leak in fdopen (bug 31840)
- Backport: libio: Test for fdopen memory leak without SEEK_END
  support (bug 31840)

Resolves: RHEL-108475
swbz#31840
RPM-Release: no
]])
      assert(not t)
      assert(err == 'malformed line in Git trailer after Resolves tag')
   end
end

-- Produce a list of changelog messages.  The list can be empty.  Use
-- trailer.rpm_changelog if available.
local function rpm_changelog_default(message, trailer)
   if trailer.rpm_changelog then
      return trailer.rpm_changelog
   end
   local subject = assert(string.match(message, '^%s*([^\n]-)%s*\n'))
   -- See if there are tickets listed in parentheses.
   local parens = string.match(subject, '%s+[(]([^)]+)[)]%s*$')
   local tickets = trailer.tickets
   if (not (parens and parse_ticket_string('subject', parens))
       and tickets and #tickets > 0) then
      subject = subject .. ' (' .. table.concat(tickets, ', ') .. ')'
   end
   local result = {}
   append_to_rpm_changelog(subject, result)
   return result
end
-- Tests for rpm_changelog_default.
do
   local t
   local function rcd(message)
      return rpm_changelog_default(message, assert(parse_trailer(message)))
   end
   t = rcd([[Remove memory leak in fdopen

Resolves: RHEL-108475
]])
   assert_eq(t, {'- Remove memory leak in fdopen (RHEL-108475)'})

   t = rcd([[Remove memory leak in fdopen (RHEL-108475)

Resolves: RHEL-108475
]])
   assert_eq(t, {'- Remove memory leak in fdopen (RHEL-108475)'})

   t = rcd([[Remove memory leak in fdopen (RHEL-108475)

Resolves: RHEL-108475
RPM-Changelog: -
]])
   assert(#t == 0)

   t = rcd([[Remove memory leak in fdopen

Resolves: RHEL-108475
RPM-Changelog:
 - Remove memory leak in fdopen (bug 31840)
 - libio: Test for fdopen memory leak without SEEK_END
]])
   assert_eq(t,
             {'- Remove memory leak in fdopen (bug 31840)',
              '- libio: Test for fdopen memory leak without SEEK_END'})

   t = rcd([[Do not wrap the cat

Resolves: RHEL-108475
RPM-Changelog:
  - Do not wrap the cat!
     /\_/\
    ( o.o )
     > ^ <
  - Thank you.
]])
   assert_eq(t,
             {'- Do not wrap the cat!',
              [[   /\_/\]],
              [[  ( o.o )]],
              [[   > ^ <]],
              '- Thank you.'})

   t = rcd([[Do not wrap the cat

Resolves: RHEL-108475
RPM-Changelog:
 - Do not wrap the cat!
    /\_/\
   ( o.o )
    > ^ <
 - Thank you.
]])
   assert_eq(t,
             {'- Do not wrap the cat!',
              [[   /\_/\]],
              [[  ( o.o )]],
              [[   > ^ <]],
              '- Thank you.'})

   t = rcd([[Do not wrap the cat

Resolves: RHEL-108475
RPM-Changelog:
 - Do not wrap the cat!
    /\_/\
   ( o.o )
    > ^ <
]])
   assert_eq(t,
             {[[- Do not wrap the cat!]],
              [[   /\_/\]],
              [[  ( o.o )]],
              [[   > ^ <]]})

   -- Variant that has the dash on the RPM-Changelog line.
   t = rcd([[Do not wrap the cat

Resolves: RHEL-108475
RPM-Changelog: - Do not wrap the cat!
    /\_/\
   ( o.o )
    > ^ <
]])
   assert_eq(t,
             {[[- Do not wrap the cat!]],
              [[   /\_/\]],
              [[  ( o.o )]],
              [[   > ^ <]]})
end


-- Turns a commit message into a string for diagnostic purposes.
local function commit_to_string(commit)
   local result = {
      'commit ' .. commit.commit .. '\n',
      'Author: ' .. commit.author .. '\n',
      'Date:   ' .. commit.author_date .. '\n',
      '\n',
   }
   -- Indent the commit message by four spaces.
   for line in string.gmatch(commit.message, '([^\n]*\n)') do
      result[#result + 1] = '    ' .. line
   end
   return table.concat(result)
end
-- Abort execution after logging the commit message to stderr.
local function assert_commit(commit, cond, ...)
   if cond then
      -- Return all function arguments except the first.
      return cond, ...
   end
   local message = ... -- Extract first variadic argument.
   local err = message or 'assertion failure'
   io.stderr:write('error in commit message: ' .. err .. '\n\n'
                   .. commit_to_string(commit)
                   .. '\n')
   error(err)
end
-- Test for assert_commit.
assert(3 == #{assert_commit(false, 1, 2, 3)})

-- Go through the relevant commits in patchgit.commits.  Set
-- patchgit.start_commit_index_for_changelog and
-- patchgit.start_commit_index for future use by process_commits below.
local function parse_commit_messages()
   -- If already invoked, do not parse the commits again.
   if patchgit.start_commit_index then
      return
   end

   local commits = patchgit.commits

   -- Cache the parsed trailers for forward traversal.
   local trailers = {}
   local start_commit = 1

   local patchgit_version

   -- These are set to true once enough commits have been found to
   -- compute their values.
   local version_known = false
   local release_known = false
   local changelog_known = false

   for i=#patchgit.commits,1,-1 do
      local commit = patchgit.commits[i]

      local trailer = assert_commit(commit, parse_trailer(commit.message))
      if trailer.parent then
         if i == 1 then
            assert_commit(commit, false, 'Parent tag in commit without parent')
         elseif commits[i - 1].commit ~= trailer.parent then
            assert_commit(commit, false, 'found unexpected parent commit '
                          .. commits[i - 1].commit)
         end
      end

      trailers[i] = trailer

      patchgit_version = trailer.patchgit_version
      if patchgit_version then
         assert_commit(commit, patchgit_version == 1,
                       'unsupport patch-git version ' .. patchgit_version)
      end

      -- Stop iterating if all data can be determined from the commits seen.
      if trailer.rpm_version then
         version_known = true
      end
      if trailer.rpm_release then
         release_known = true
      end
      if trailer.rpm_changelog_stop then
         changelog_known = true
         if not patchgit.start_commit_index_for_changelog then
            patchgit.start_commit_index_for_changelog = i
         end
      end

      -- A Patch-Git-Version commit on its own does not tell us how to
      -- interpret previous history.  The first commit setting version/release
      -- must also set the patch-git version.
      if patchgit_version
         and patchgit_version and release_known and changelog_known
      then
         start_commit = i
         break
      end
   end

   assert_commit(commits[1], patchgit_version, 'RPM version not determined')
   assert_commit(commits[1], version_known, 'RPM version not determined')
   assert_commit(commits[1], release_known, 'RPM release not determined')

   assert(patchgit.start_commit_index_for_changelog)
   patchgit.start_commit_index = start_commit
   patchgit.commit_trailers = trailers
end

--
-- Returns a YYYY-MM-DD formatted date as the second result.
local git_date_to_rpm_date
do
   local months = {
      Jan=1,
      Feb=2,
      Mar=3,
      Apr=4,
      May=5,
      Jun=6,
      Jul=7,
      Aug=8,
      Sep=9,
      Oct=10,
      Nov=11,
      Dec=12,
   }
   function git_date_to_rpm_date(s)
   local wd, mon, d, y = string.match(
      s, '^([A-z][a-z][a-z]) ([A-Z][a-z][a-z]) (%d+) %d%d:%d%d:%d%d (%d+)')
   assert(y, s)
   local m = assert(months[mon], s)
   local rpmdate = string.format('%s %s %02d %04d', wd, mon, d, y)
   local ymd = string.format('%04d-%02d-%02d', y, m, d)
   return rpmdate, ymd
   end
end
-- Tests for git_date_to_rpm_date.
do
   local rpmdate, ymd
   local rpmdate, ymd = assert(git_date_to_rpm_date(
                                  'Wed Jul 23 09:14:49 2025 +0200'))
   assert(rpmdate == 'Wed Jul 23 2025')
   assert(ymd == '2025-07-23')
end

-- Quote RPM macro invocations in s and return the string.
local function rpm_quote(s)
   -- Parentheses are needed to elide the second return value of string.gsub.
   return (string.gsub(s, '%%', '%%%%'))
end
-- Tests for rpm_quote.
do
   assert(rpm_quote('') == '')
   assert(rpm_quote('abc') == 'abc')
   assert(rpm_quote('%abc') == '%%abc')
   assert(rpm_quote('a%bc') == 'a%%bc')
   assert(rpm_quote('ab%c') == 'ab%%c')
   assert(rpm_quote('abc%') == 'abc%%')
   assert(rpm_quote('%%abc') == '%%%%abc')
   assert(rpm_quote('a%%bc') == 'a%%%%bc')
   assert(rpm_quote('ab%%c') == 'ab%%%%c')
   assert(rpm_quote('abc%%') == 'abc%%%%')
end

-- If changelog is not nil, it is used as a table of tables for
-- changelog entries.
local function process_commits(changelog, changelog_after_commit)
   parse_commit_messages()

   local commits = patchgit.commits
   local start_changelog = assert(patchgit.start_commit_index_for_changelog)
   local trailers = assert(patchgit.commit_trailers)

   local rpm_version

   -- rpm_release_num is the rightmost number that needs to be
   -- incremented for new RPM releases.  Call set_release to change
   -- and get_release to read.
   local rpm_release_pre, rpm_release_num, rpm_release_post
   local function set_release(rel)
      rpm_release_pre, rpm_release_num, rpm_release_post =
         assert_commit(commit, string.match(rel, '^(.-)(%d+)([^%d]*)$'))
   end
   local function get_release()
      return rpm_release_pre .. rpm_release_num .. rpm_release_post
   end

   local on_zstream = false
   local last_changelog_rpmdate
   local last_changelog_ymd

   -- This is set to true once changelog_after_commit is found
   -- as a commit hash.
   local include_commits_in_changelog = not changelog_after_commit
   assert(not changelog_after_commit or #changelog_after_commit == 40)

   for i=assert(patchgit.start_commit_index), #commits do
      local commit = commits[i]
      local trailer = trailers[i]
      local zstream_switch_request = trailer.rpm_branch_type == 'zstream'

      if trailer.rpm_version then
        rpm_version = trailer.rpm_version
        -- The version gets incremented below.
        if on_zstream or zstream_switch_request then
           set_release('1%{?dist}.0')
           zstream_switch_request = false
        else
           set_release('0%{?dist}')
        end
     end

     if trailer.rpm_release then
         set_release(trailer.rpm_release)
         assert_commit(commit, get_release() == trailer.rpm_release,
                       'RPM release parsing')
         on_zstream = zstream_switch_request
         -- Do not bump the release below.
      else
         if zstream_switch_request and not on_zstream then
            assert_commit(commit, rpm_release_num,
                          'RPM release not determined for zstream')
            -- ZStream NVR policy: Release counter follows %{?dist}.
            set_release(get_release() .. '.0')
            on_zstream = true
         end
         if not trailer.rpm_skip_release then
            assert_commit(commit, rpm_release_num, 'RPM release not determined')
            rpm_release_num = rpm_release_num + 1
         end
      end

      if changelog then
	 if not include_commits_in_changelog then
	    if commit.commit == changelog_after_commit then
	       -- Start including commits after this one.
	       include_commits_in_changelog = true
	    end
	 else
	    local cl_entries = assert_commit(
	       commit, rpm_changelog_default(commit.message, trailer))
	    if #cl_entries > 0 then
	       -- The changelog list where the new entries are inserted.
	       local target_cl = changelog[#changelog]

	       if not trailer.rpm_skip_release then
		  -- Changelog is not skipped.  Generate a new header.
		  -- Use commit date because it gets updated when
		  -- cherry-picking.  Avoid going backwards in time
		  -- because it generates warnings from RPM.
		  local rpmdate, ymd = git_date_to_rpm_date(commit.commit_date)
		  if last_changelog_ymd and ymd < last_changelog_ymd then
		     rpmdate = last_changelog_rpmdate
		     ymd = last_changelog_ymd
		  end
		  local author = commit.author
		  -- The %changelog section does not include the %dist macro.
		  local rpmrel = string.gsub(get_release(), '%%{%?dist}', '')
		  assert(not string.find(rpmrel, '%', 1, true), rpmrel)
		  local hdr = '* ' .. rpmdate .. ' ' .. author .. ' - '
		     .. rpm_version .. '-' .. rpmrel

		  -- Append a new changelog list.
		  target_cl = {hdr}
		  changelog[#changelog + 1] = target_cl
	       end

	       -- Insert the changelog entries into the previous
	       -- changelog, at the end.  No direct move because of %
	       -- quoting.  If no new entry was inserted above, but we
	       -- switched to zstream, this adds to an entry that does not
	       -- have the expected release, which is a minor inconsistency.
	       assert_commit(commit,
			     target_cl and #target_cl > 0,
			     'first commit skips changelog and has an entry')
	       table.move(cl_entries, 1, #cl_entries,
			  #target_cl + 1, target_cl)
	    end
	 end
      end
   end

   assert_commit(commits[#commits], rpm_version,
                 'RPM version not determined for HEAD')
   assert_commit(commits[#commits], rpm_release_num,
                 'RPM release not determined for HEAD')
   patchgit.rpm_version = rpm_version
   patchgit.rpm_release = get_release()
end

----------------------------------------------------------------------
-- Launching the actual work, and command line handling
----------------------------------------------------------------------

if rpm then
   -- If running under rpm, generate the missing parts of the spec file.
   generate_files()
   parse_commits()

   function patchgit.release()
      process_commits()
      print(rpm.expand(patchgit.rpm_release))
   end
   function patchgit.version()
        process_commits()
        print(rpm.expand(patchgit.rpm_version))
   end
   function patchgit.changelog()
      -- This can be defined to extract the final set of patches from
      -- the spec file in a programmable manner.  It is a replacement
      -- for rpmspec --eval, which does not work as expected because
      -- it is not evaluated in the context of the patch file.  Do
      -- this from the changelog writing procedure because at this
      -- point, all Patch: directives in the spec file definitely have
      -- been processed, so the patches global variable has been
      -- populated.
      local patches_log = rpm.expand('%{?_patchgit_log_patches}')
      if patches_log ~= '' then
         local fp = assert(io.open(patches_log, 'w+'))
         for i=1,#patches do
            local pname = assert(string.match(patches[i], '.*/([^/]+)$'))
            fp:write('Patch' .. i .. ': ' .. pname .. '\n')
         end
         assert(fp:close())
      end

      local changelog = {}
      process_commits(changelog)
      for i=#changelog,1,-1 do
         local cl = changelog[i]
         for j=1,#cl do
	    -- RPM does not recursively macro-expand what we emit here,
	    -- so do not apply %-escaping.
            print(cl[j], '\n')
         end
         print('\n')
      end
   end
else
   local args = {...}
   if #args == 0 then
      args[1] = 'help'
   end
   local cmds = {}
   function cmds.help()
      print([[Available subcommands:
    help       this output
    patches    print list of PatchNNN: directives
    version    print the value of the computed RPM version at HEAD
    release    print the value of the computed RPM release at HEAD
    verrel     print the value of RPM version-release
    changelog  show the auto-generated changelog entries]])
   end
   function cmds.patches(flag, extra)
      if extra then
         error('unrecognized argument: ' .. extra)
      end
      if flag and flag ~= '--history-only' then
         error('unrecognized argument: ' .. flag)
      end
      generate_files()
      parse_commits()
      if flag == '--history-only' then
         -- Only print the patches that come from the Git history.
         patchgit.patches({history_only=true})
      else
         -- There does not seem to be a way to do this in a better way.
         -- Instruct one of the patch-git macros to write a temporary file.
         with_temporary_file(
	    function(tmpfile)
               check_rpmspec(get_single_spec_file(),
                             '-D _patchgit_log_patches ' .. tmpfile,
                             '-q', '--srpm', '--qf', '')
               local fp = assert(io.open(tmpfile, 'r'))
               assert(io.stdout:write(assert(fp:read('a'))))
               assert(fp:close())
            end)
      end
   end
   function cmds.version()
      generate_files()
      parse_commits()
      process_commits()
      print(patchgit.rpm_version)
   end
   function cmds.release()
      generate_files()
      parse_commits()
      process_commits()
      print(patchgit.rpm_release)
   end
   function cmds.verrel()
      generate_files()
      parse_commits()
      process_commits()
      print(patchgit.rpm_version .. '-' .. patchgit.rpm_release)
   end
   function cmds.changelog(start_commit)
      if start_commit then
	 start_commit =
	    assert(string.match(run_git('rev-parse '
					.. shell_quote(start_commit)),
				'^([^\n]+)\n'))
      end
      generate_files()
      parse_commits()
      local changelog = {}
      process_commits(changelog, start_commit)
      for i=#changelog,1,-1 do
         local cl = changelog[i]
         for j=1,#cl do
	    -- Apply %-escaping here, so that the output can be copy-pasted
	    -- into %changelog.
            print(rpm_quote(cl[j]))
         end
         print()
      end
   end
   function cmds.selftest()
      -- Hidden command to run all subcommands.
      local test_commands = {'patches --history-only',
			     'changelog HEAD^'}
      for k, _ in pairs(cmds) do
         if k ~= 'selftest' then
            test_commands[#test_commands + 1] = k
         end
      end
      table.sort(test_commands)
      local failure
      for _, cmd in ipairs(test_commands) do
         cmd = 'lua patch-git.lua ' .. cmd
         print('* ' .. cmd)
         local ok, term, status = os.execute(cmd)
         if not ok or term ~= 'exit' or status ~= 0 then
            failure = true
            print('FAIL: term=' .. term .. ', status=' .. status)
         end
      end
      if fail then
         os.exit(1)
      end
   end
   local cmd = cmds[args[1]]
   if not cmd then
      io.stderr:write('usage: Unrecognized command "' .. args[1]
                      .. '".  Use "help" for a list of commands.\n')
      os.exit(1)
   end
   cmd(table.unpack(args, 2))
end
