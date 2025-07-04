import os
from pathlib import Path

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import chdir, copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.1"


class EmSDKConan(ConanFile):
    name = "emsdk"
    description = "Emscripten SDK. Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kripken/emscripten"
    topics = ("emsdk", "emscripten", "sdk", "emcc", "em++", "nodejs")
    license = "MIT"
    package_type = "application"
    settings = "os", "arch"
    upload_policy = "skip"
    build_policy = "missing"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _relative_paths(self):
        return ["bin", os.path.join("bin", "upstream", "emscripten")]

    @property
    def _paths(self):
        return [os.path.join(self.package_folder, path) for path in self._relative_paths]

    @property
    def _emsdk(self):
        return os.path.join(self.package_folder, "bin")

    @property
    def _emscripten(self):
        return os.path.join(self.package_folder, "bin", "upstream", "emscripten")

    @property
    def _em_config(self):
        return os.path.join(self.package_folder, "bin", ".emscripten")

    @property
    def _em_cache(self):
        return os.path.join(self.package_folder, "bin", ".emscripten_cache")

    @property
    def _node_path(self):
        subfolders = [path for path in (Path(self.package_folder) / "bin" / "node").iterdir() if path.is_dir()]
        if len(subfolders) != 1:
            return None
        return os.path.join("bin", "node", subfolders[0].name, "bin")

    def generate(self):
        env = Environment()
        env.prepend_path("PATH", self._paths)
        env.define_path("EMSDK", self._emsdk)
        env.define_path("EMSCRIPTEN", self._emscripten)
        env.define_path("EM_CONFIG", self._em_config)
        env.define_path("EM_CACHE", self._em_cache)
        env.vars(self, scope="emsdk").save_script("emsdk_env_file")

        # To avoid issues when cross-compiling or with not common arch in profiles we need to set EMSDK_ARCH
        # This is important for the emsdk install command
        env = VirtualBuildEnv(self)
        # Special consideration for armv8 as emsdk expects "arm64"
        arch = "arm64" if str(self.settings.arch) == "armv8" else str(self.settings.arch)
        env.environment().define("EMSDK_ARCH", arch)
        env.generate()

    def build(self):
        with chdir(self, self.source_folder):
            emsdk = "emsdk.bat" if self.settings_build.os == "Windows" else "./emsdk"
            self.run(f"{emsdk} install latest")
            self.run(f"{emsdk} activate latest")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        if not cross_building(self):
            self.run("embuilder build MINIMAL", env=["conanemsdk", "conanrun"])  # force cache population
            # Avoid cache failures in case this package is uploaded as paths in sanity.txt are absolute
            os.remove(os.path.join(self._em_cache, "sanity.txt"))

    def _define_tool_var(self, value):
        suffix = ".bat" if self.settings.os == "Windows" else ""
        path = os.path.join(self._emscripten, f"{value}{suffix}")
        return path

    def package_info(self):
        self.cpp_info.bindirs = self._relative_paths + [self._node_path]
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # If we are not building for Emscripten, probably we don't want to inject following environment variables,
        #   but it might be legit use cases... until we find them, let's be conservative.
        if not hasattr(self, "settings_target") or self.settings_target is None:
            return

        if self.settings_target.os != "Emscripten":
            self.output.warning(
                f"You've added {self.name}/{self.version} as a build requirement, while os={self.settings_target.os} != Emscripten"
            )
            return

        toolchain = os.path.join(
            self.package_folder, "bin", "upstream", "emscripten", "cmake", "Modules", "Platform", "Emscripten.cmake"
        )
        self.conf_info.prepend("tools.cmake.cmaketoolchain:user_toolchain", toolchain)

        self.buildenv_info.define_path("EMSDK", self._emsdk)
        self.buildenv_info.define_path("EMSCRIPTEN", self._emscripten)
        self.buildenv_info.define_path("EM_CONFIG", self._em_config)
        self.buildenv_info.define_path("EM_CACHE", self._em_cache)

        compiler_executables = {
            "c": self._define_tool_var("emcc"),
            "cpp": self._define_tool_var("em++"),
        }
        self.conf_info.update("tools.build:compiler_executables", compiler_executables)
        self.buildenv_info.define_path("CC", compiler_executables["c"])
        self.buildenv_info.define_path("CXX", compiler_executables["cpp"])
        self.buildenv_info.define_path("AR", self._define_tool_var("emar"))
        self.buildenv_info.define_path("NM", self._define_tool_var("emnm"))
        self.buildenv_info.define_path("RANLIB", self._define_tool_var("emranlib"))
        self.buildenv_info.define_path("STRIP", self._define_tool_var("emstrip"))
