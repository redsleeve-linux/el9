/* Copyright (C) 2019 Free Software Foundation, Inc.
   Contributed by Jakub Jelinek <jakub@redhat.com>.

   This file is part of the GNU Offloading and Multi Processing Library
   (libgomp).
  
   Libgomp is free software; you can redistribute it and/or modify it
   under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   Libgomp is distributed in the hope that it will be useful, but WITHOUT ANY
   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
   FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
   more details.

   Under Section 7 of GPL version 3, you are granted additional
   permissions described in the GCC Runtime Library Exception, version
   3.1, as published by the Free Software Foundation.

   You should have received a copy of the GNU General Public License and
   a copy of the GCC Runtime Library Exception along with this program;
   see the files COPYING3 and COPYING.RUNTIME respectively.  If not, see
   <http://www.gnu.org/licenses/>.  */

/* Remapping of nonmonotonic runtime schedule and maybe nonmonotonic runtime
   schedule loop entrypoints (the used by GCC 9 and later for runtime
   schedule without monotonic or nonmonotonic modifiers).
   RHEL 7 libgomp only implements the GOMP*loop*runtime* entrypoints without
   nonmonotonic in the names, which always implement monotonic scheduling,
   but the library doesn't implement any other scheduling, even in GCC 9
   and monotonic scheduling is a valid implementation of non-monotonic
   scheduling.  */

#include <stdbool.h>

typedef unsigned long long ull;
extern bool GOMP_loop_runtime_start (long, long, long, long *, long *);
extern bool GOMP_loop_runtime_next (long *, long *);
extern void GOMP_parallel_loop_runtime (void (*)(void *), void *,
					unsigned, long, long, long,
					unsigned);
extern bool GOMP_loop_ull_runtime_start (bool, ull, ull, ull, ull *, ull *);
extern bool GOMP_loop_ull_runtime_next (ull *, ull *);
extern bool GOMP_loop_dynamic_next (long *, long *);
extern bool GOMP_loop_dynamic_start (long, long, long, long, long *, long *);
extern bool GOMP_loop_guided_next (long *, long *);
extern bool GOMP_loop_guided_start (long, long, long, long, long *, long *);
extern bool GOMP_loop_ull_dynamic_next (ull *, ull *);
extern bool GOMP_loop_ull_dynamic_start (bool, ull, ull, ull, ull, ull *,
					 ull *);
extern bool GOMP_loop_ull_guided_next (ull *, ull *);
extern bool GOMP_loop_ull_guided_start (bool, ull, ull, ull, ull, ull *,
					ull *);
extern void GOMP_parallel_loop_dynamic (void (*)(void *), void *,
					unsigned, long, long, long, long,
					unsigned);
extern void GOMP_parallel_loop_guided (void (*)(void *), void *,
				       unsigned, long, long, long, long,
				       unsigned);
#define alias(x, y) __typeof (x) y __attribute__((alias (#x)))

#pragma GCC visibility push(hidden)

bool
GOMP_loop_nonmonotonic_runtime_start (long start, long end, long incr,
				      long *istart, long *iend)
{
  return GOMP_loop_runtime_start (start, end, incr, istart, iend);
}
alias (GOMP_loop_nonmonotonic_runtime_start,
       GOMP_loop_maybe_nonmonotonic_runtime_start);

bool
GOMP_loop_nonmonotonic_runtime_next (long *istart, long *iend)
{
  return GOMP_loop_runtime_next (istart, iend);
}
alias (GOMP_loop_nonmonotonic_runtime_next,
       GOMP_loop_maybe_nonmonotonic_runtime_next);

void
GOMP_parallel_loop_nonmonotonic_runtime (void (*fn)(void *), void *data,
					 unsigned num_threads, long start,
					 long end, long incr, unsigned flags)
{
  return GOMP_parallel_loop_runtime (fn, data, num_threads, start,
				     end, incr, flags);
}
alias (GOMP_parallel_loop_nonmonotonic_runtime,
       GOMP_parallel_loop_maybe_nonmonotonic_runtime);

bool
GOMP_loop_ull_nonmonotonic_runtime_start (bool up, ull start, ull end,
					  ull incr, ull *istart, ull *iend)
{
  return GOMP_loop_ull_runtime_start (up, start, end, incr, istart, iend);
}
alias (GOMP_loop_ull_nonmonotonic_runtime_start,
       GOMP_loop_ull_maybe_nonmonotonic_runtime_start);

bool
GOMP_loop_ull_nonmonotonic_runtime_next (ull *istart, ull *iend)
{
  return GOMP_loop_ull_runtime_next (istart, iend);
}
alias (GOMP_loop_ull_nonmonotonic_runtime_next,
       GOMP_loop_ull_maybe_nonmonotonic_runtime_next);

bool
GOMP_loop_nonmonotonic_dynamic_next (long *istart, long *iend)
{
  return GOMP_loop_dynamic_next (istart, iend);
}

bool
GOMP_loop_nonmonotonic_dynamic_start (long start, long end, long incr,
				      long chunk_size, long *istart,
				      long *iend)
{
  return GOMP_loop_dynamic_start (start, end, incr, chunk_size, istart, iend);
}

bool
GOMP_loop_nonmonotonic_guided_next (long *istart, long *iend)
{
  return GOMP_loop_guided_next (istart, iend);
}

bool
GOMP_loop_nonmonotonic_guided_start (long start, long end, long incr,
				     long chunk_size, long *istart, long *iend)
{
  return GOMP_loop_guided_start (start, end, incr, chunk_size, istart, iend);
}

bool
GOMP_loop_ull_nonmonotonic_dynamic_next (ull *istart, ull *iend)
{
  return GOMP_loop_ull_dynamic_next (istart, iend);
}

bool
GOMP_loop_ull_nonmonotonic_dynamic_start (bool up, ull start,
					  ull end, ull incr,
					  ull chunk_size,
					  ull *istart, ull *iend)
{
  return GOMP_loop_ull_dynamic_start (up, start, end, incr, chunk_size, istart,
				      iend);
}

bool
GOMP_loop_ull_nonmonotonic_guided_next (ull *istart, ull *iend)
{
  return GOMP_loop_ull_guided_next (istart, iend);
}

bool
GOMP_loop_ull_nonmonotonic_guided_start (bool up, ull start, ull end,
					 ull incr, ull chunk_size,
					 ull *istart, ull *iend)
{
  return GOMP_loop_ull_guided_start (up, start, end, incr, chunk_size, istart,
				     iend);
}

void
GOMP_parallel_loop_nonmonotonic_dynamic (void (*fn) (void *), void *data,
					 unsigned num_threads, long start,
					 long end, long incr, long chunk_size,
					 unsigned flags)
{
  GOMP_parallel_loop_dynamic (fn, data, num_threads, start, end, incr,
			      chunk_size, flags);
}

void
GOMP_parallel_loop_nonmonotonic_guided (void (*fn) (void *), void *data,
					unsigned num_threads, long start,
					long end, long incr, long chunk_size,
					unsigned flags)
{
  GOMP_parallel_loop_guided (fn, data, num_threads, start, end, incr,
			     chunk_size, flags);
}

#pragma  GCC visibility pop
