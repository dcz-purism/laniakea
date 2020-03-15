module pywrap;

// We only add the Python bindings if not in unittest mode
version(unittest) {}
else {

import pyd.pyd;
import pyd.embedded;
import lknative.py.pyhelper;

import lknative.utils : SignedFile, compareVersions;
import lknative.utils.namegen : generateName;
import lknative.logging : setVerboseLog;
import lknative.config;

extern(C) void PydMain()
{
    /* Common */
    def!(compareVersions, PyName!"compare_versions")();
    def!(generateName, PyName!"generate_name")();
    def!(setVerboseLog, PyName!"logging_set_verbose")();

    module_init();

    /* Common */
    wrap_class!(SignedFile,
            Init!(string[]),

            Def!(SignedFile.open),
    )();

    wrapAggregate!(BaseConfig)();
    wrapAggregate!(BaseArchiveConfig)();
    wrapAggregate!(SuiteInfo)();
    wrapAggregate!(ParentSuiteInfo)();

    /* Repo infrastructure */
    import lknative.repository;
    wrapAggregate!(ArchiveFile)();
    wrapAggregate!(SourcePackage)();
    wrapAggregate!(BinaryPackage)();
    wrapAggregate!(PackageInfo)();
    wrap_class!(Repository,
            Init!(string, string, string, string[]),

            Def!(Repository.getSourcePackages),
            Def!(Repository.getBinaryPackages),
            Def!(Repository.getInstallerPackages),
            Def!(Repository.getIndexFile),
    )();
    wrap_class!(SignedFile,
            Init!(string[]),

            Def!(SignedFile.open),
            Def!(SignedFile.isValid),
            Def!(SignedFile.fingerprint),
            Def!(SignedFile.primaryFingerprint),
            Def!(SignedFile.signatureId),
            Def!(SignedFile.content),
    )();

    /* Synchrotron */
    import lknative.synchrotron;
    wrapAggregate!(SyncSourceSuite)();
    wrapAggregate!(SyncSourceInfo)();
    wrapAggregate!(SynchrotronConfig)();
    wrapAggregate!(SynchrotronIssue)();
    wrap_class!(SyncEngine,
            Init!(BaseConfig, SynchrotronConfig, SuiteInfo),

            Def!(SyncEngine.setSourceSuite),
            Def!(SyncEngine.setBlacklist),

            Def!(SyncEngine.autosync),
            Def!(SyncEngine.syncPackages),

            Def!(SyncEngine.getSyncedSourcePackages),
    )();
}


import deimos.python.object: PyObject;
extern(C) export PyObject* PyInit_lknative() {
    import pyd.thread : ensureAttached;
    return pyd.exception.exception_catcher(delegate PyObject*() {
        ensureAttached();
        pyd.def.pyd_module_name = "lknative";
        PydMain();
        return pyd.def.pyd_modules[""];
    });
}

extern(C) void _Dmain(){
    // make druntime happy
}

} // End of unittest conditional
