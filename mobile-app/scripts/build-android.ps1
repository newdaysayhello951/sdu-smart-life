param(
 [ValidateSet('Debug','Release')][string]$Configuration='Debug',
 [string]$JavaHome=$env:JAVA_HOME,
 [string]$AndroidSdk=$env:ANDROID_HOME,
 [string]$GradleCommand,
 [string]$Proxy
)
$ErrorActionPreference='Stop'
$mobileRoot=Split-Path -Parent $PSScriptRoot
$repoRoot=Split-Path -Parent $mobileRoot
if(!$JavaHome -or !(Test-Path -LiteralPath (Join-Path $JavaHome 'bin/java.exe'))){throw 'Set JAVA_HOME to a Java 21 JDK (Android Studio jbr is supported).'}
if(!$AndroidSdk){$AndroidSdk=Join-Path $env:LOCALAPPDATA 'Android/Sdk'}
if(!(Test-Path -LiteralPath (Join-Path $AndroidSdk 'platforms/android-35'))){throw 'Install Android SDK Platform 35 first.'}
$env:JAVA_HOME=$JavaHome
$env:ANDROID_HOME=$AndroidSdk
$env:GRADLE_USER_HOME=Join-Path $repoRoot '.tools/mobile-gradle'
$gradleArgs=@('-p',(Join-Path $mobileRoot 'android'),':app:clean',('assemble'+$Configuration),'--max-workers=2','--console=plain','--no-daemon')
if($Proxy){$proxyUri=[Uri]$Proxy;if($proxyUri.UserInfo -or !$proxyUri.Host -or $proxyUri.Scheme -ne 'http'){throw 'Proxy must be an HTTP proxy URL without credentials.'};$gradleArgs+=@("-Dhttps.proxyHost=$($proxyUri.Host)","-Dhttps.proxyPort=$($proxyUri.Port)","-Dhttp.proxyHost=$($proxyUri.Host)","-Dhttp.proxyPort=$($proxyUri.Port)")}
Push-Location $mobileRoot
try {
 if($Configuration -eq 'Debug'){& npm.cmd run android:sync:debug}else{& npm.cmd run android:sync}
 if($LASTEXITCODE -ne 0){throw 'Web build or Capacitor sync failed.'}
 if(!$GradleCommand){$GradleCommand=Join-Path $mobileRoot 'android/gradlew.bat'}
 & $GradleCommand @gradleArgs
 if($LASTEXITCODE -ne 0){throw 'Android build failed.'}
 Write-Output (Join-Path $mobileRoot ('android/app/build/outputs/apk/'+$Configuration.ToLower()))
}finally{Pop-Location}
