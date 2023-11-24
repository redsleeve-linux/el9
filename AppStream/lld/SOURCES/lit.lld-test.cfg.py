#Clear lld_tools_dir so we don't accidently pick up tools from somewhere else
config.lld_tools_dir = ""

if hasattr(config, 'have_zlib'):
    # Regression tests write output to this directory, so we need to be able to specify
    # a temp directory when invoking lit. e.g. lit -Dlld_obj_root=/tmp/lit
    config.lld_obj_root = "%(lld_obj_root)s" % lit_config.params
    lit_config.load_config(config, '%(lld_test_root)s/lit.cfg.py' % lit_config.params)
else:
    # For unit tests, llvm_obj_root is used to find the unit test binaries.
    config.lld_obj_root = '%(lld_unittest_bindir)s' % lit_config.params
    lit_config.load_config(config, '%(lld_test_root)s/Unit/lit.cfg.py' % lit_config.params)
