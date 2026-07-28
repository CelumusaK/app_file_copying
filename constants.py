IGNORED = {
    # Version Control
    ".git", ".gitignore", ".gitattributes",
    
    # IDE/Editor
    ".idea", ".vscode", ".editorconfig", ".DS_Store", ".venv",
    
    # Flutter/Dart Build
    ".dart_tool", ".flutter-plugins", ".flutter-plugins-dependencies",
    ".metadata", ".packages", "build", ".gradle", ".kotlin",
    "*.iml", "*.g.dart", "*.freezed.dart", "*.mocks.dart",
    
    # Platform-specific build artifacts
    "android/.gradle", "android/gradle", "android/local.properties",
    "android/.kotlin", "android/gradlew", "android/gradlew.bat",
    "ios/Flutter/ephemeral", "ios/Pods", "ios/Podfile.lock",
    "macos/Flutter/ephemeral", "macos/Pods",
    "linux/flutter/ephemeral", "windows/flutter/ephemeral",
    
    # Generated files
    "generated_plugin_registrant.dart", "generated_plugins.cmake",
    "GeneratedPluginRegistrant.java", "GeneratedPluginRegistrant.swift",
    "GeneratedPluginRegistrant.h", "GeneratedPluginRegistrant.m",
    
    # Node/JS
    "node_modules", ".yarn", ".turbo", "dist",
    "*.lock", "yarn.lock", "package-lock.json",
    
    # Logs and temp
    "*.log", "*.pyc", "__pycache__", ".cache", ".cookie",
    ".expo", "*.swp", "*.bak",
    
    # Environment
    ".env", ".env.local",
    
    # Binary/Media
    "*.png", "*.jpg", "*.jpeg", "*.ico", "*.jar",
    "*.exe", "*.dll", "*.so", "*.dylib", "flutter_export_environment.sh",
    "AppFrameworkInfo.plist", "ephemeral", ".plugin_symlinks",
    "gradle-wrapper.jar", "gradle-wrapper.properties",
    
    # Xcode/Native
    "*.xcworkspace", "*.xcodeproj", "xcshareddata",
    "IDEWorkspaceChecks.plist", "WorkspaceSettings.xcsettings",
    "test_driver", "integration_test",
    "*.rc", "*.manifest", "runner.exe.manifest",
    "CMakeLists.txt", "*.cmake",
    "migrate.py", "history.json", "update_id.py",
}

SKIP_DIRS = {
    ".dart_tool", ".gradle", ".idea", "build", "ephemeral",
    ".plugin_symlinks", "Pods", "node_modules", "__pycache__", ".git",
    "linux/flutter/ephemeral", "windows/flutter/ephemeral",
    "macos/Flutter/ephemeral", "ios/Flutter/ephemeral",
}