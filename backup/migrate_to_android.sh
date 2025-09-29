#!/bin/bash

# Replit to Android SDK Migration Script
# This script converts your Replit project to use Android SDK

set -e  # Exit on any error

echo "🚀 Starting Replit to Android SDK migration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Replit
if [ ! -f ".replit" ]; then
    print_warning "No .replit file found. This script is designed for Replit projects."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Backup existing files
print_status "Creating backup of existing configuration..."
mkdir -p backup
cp -r * backup/ 2>/dev/null || true

# Get project details
read -p "Enter your app name (default: MyApp): " APP_NAME
APP_NAME=${APP_NAME:-MyApp}

read -p "Enter package name (e.g., com.example.myapp): " PACKAGE_NAME
if [ -z "$PACKAGE_NAME" ]; then
    print_error "Package name is required!"
    exit 1
fi

read -p "Enter minimum SDK version (default: 21): " MIN_SDK
MIN_SDK=${MIN_SDK:-21}

read -p "Enter target SDK version (default: 34): " TARGET_SDK
TARGET_SDK=${TARGET_SDK:-34}

# Create Android project structure
print_status "Creating Android project structure..."

# Main directories
mkdir -p app/src/main/{java,res/{layout,values,drawable,mipmap-hdpi,mipmap-mdpi,mipmap-xhdpi,mipmap-xxhdpi,mipmap-xxxhdpi}}
mkdir -p app/src/androidTest/java
mkdir -p app/src/test/java

# Convert package name to directory structure
PACKAGE_DIR=$(echo $PACKAGE_NAME | tr '.' '/')
mkdir -p app/src/main/java/$PACKAGE_DIR

# Create build.gradle (Project level)
print_status "Creating project build.gradle..."
cat > build.gradle << EOF
buildscript {
    ext.kotlin_version = "1.9.10"
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.2'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:\$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
EOF

# Create build.gradle (App level)
print_status "Creating app build.gradle..."
cat > app/build.gradle << EOF
plugins {
    id 'com.android.application'
    id 'kotlin-android'
}

android {
    namespace '$PACKAGE_NAME'
    compileSdk $TARGET_SDK

    defaultConfig {
        applicationId "$PACKAGE_NAME"
        minSdk $MIN_SDK
        targetSdk $TARGET_SDK
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'

    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
EOF

# Create gradle.properties
print_status "Creating gradle.properties..."
cat > gradle.properties << EOF
# Project-wide Gradle settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
android.nonTransitiveRClass=true
EOF

# Create settings.gradle
print_status "Creating settings.gradle..."
cat > settings.gradle << EOF
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "$APP_NAME"
include ':app'
EOF

# Create AndroidManifest.xml
print_status "Creating AndroidManifest.xml..."
cat > app/src/main/AndroidManifest.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar"
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
EOF

# Create MainActivity
print_status "Creating MainActivity..."
cat > app/src/main/java/$PACKAGE_DIR/MainActivity.kt << EOF
package $PACKAGE_NAME

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
EOF

# Create main activity layout
print_status "Creating activity layout..."
cat > app/src/main/res/layout/activity_main.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/constraints/layout/constraintlayout"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello Android!"
        android:textSize="24sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

# Create strings.xml
print_status "Creating strings.xml..."
cat > app/src/main/res/values/strings.xml << EOF
<resources>
    <string name="app_name">$APP_NAME</string>
</resources>
EOF

# Create colors.xml
cat > app/src/main/res/values/colors.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
EOF

# Create .replit configuration for Android
print_status "Updating .replit configuration for Android development..."
cat > .replit << EOF
modules = ["android-sdk"]

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "./gradlew assembleDebug"]

[[ports]]
localPort = 8080
externalPort = 80
EOF

# Create replit.nix for Android SDK
print_status "Creating replit.nix for Android SDK..."
cat > replit.nix << 'EOF'
{ pkgs }: {
  deps = [
    pkgs.android-tools
    pkgs.gradle
    pkgs.jdk11
    pkgs.kotlin
  ];

  env = {
    ANDROID_HOME = "${pkgs.android-tools}/share/android-sdk";
    JAVA_HOME = "${pkgs.jdk11}";
  };
}
EOF

# Create proguard rules
touch app/proguard-rules.pro

# Create gitignore
print_status "Creating .gitignore for Android project..."
cat > .gitignore << EOF
*.iml
.gradle
/local.properties
/.idea/caches
/.idea/libraries
/.idea/modules.xml
/.idea/workspace.xml
/.idea/navEditor.xml
/.idea/assetWizardSettings.xml
.DS_Store
/build
/captures
.externalNativeBuild
.cxx
local.properties

# Replit specific
.replit
replit.nix
EOF

# Create wrapper scripts
print_status "Creating Gradle wrapper..."
mkdir -p gradle/wrapper

# Download gradle wrapper if wget is available
if command -v wget &> /dev/null; then
    print_status "Downloading Gradle wrapper..."
    wget -O gradle/wrapper/gradle-wrapper.jar https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar

    cat > gradle/wrapper/gradle-wrapper.properties << EOF
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

    cat > gradlew << 'EOF'
#!/usr/bin/env sh

# Use the Gradle wrapper to build
exec gradle/wrapper/gradle-wrapper.jar "$@"
EOF
    chmod +x gradlew
fi

# Migration summary
print_success "✅ Android SDK migration completed!"
echo
print_status "Project Structure Created:"
echo "  📁 app/src/main/java/$PACKAGE_DIR/MainActivity.kt"
echo "  📁 app/src/main/res/layout/activity_main.xml"
echo "  📁 app/build.gradle"
echo "  📁 build.gradle"
echo "  📁 AndroidManifest.xml"
echo
print_status "Next Steps:"
echo "  1. Run 'chmod +x gradlew' to make gradle executable"
echo "  2. Run './gradlew build' to build your project"
echo "  3. Run './gradlew assembleDebug' to create APK"
echo "  4. Your backup files are in the 'backup/' directory"
echo
print_warning "Note: You may need to install Android SDK components in Replit"
print_warning "Consider using Android Studio or VS Code with Android extensions for better development experience"

echo
print_success "🎉 Migration script completed successfully!"
EOF
