Set-Location "$PSScriptRoot/.."
$maven = "$PWD/.tools/apache-maven-3.9.9/bin/mvn.cmd"
if (Test-Path $maven) { & $maven -f backend/pom.xml spring-boot:run } else { mvn -f backend/pom.xml spring-boot:run }
