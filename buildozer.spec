[app]

title = MySchedule

package.name = myschedule

package.domain = org.andreinoskov

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 1.0

requirements = python3,kivy

orientation = portrait

fullscreen = 0

android.api = 36

android.minapi = 24

android.ndk = 28c

android.ndk_api = 24

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

android.debug_artifact = apk

android.release_artifact = aab


[buildozer]

log_level = 2

warn_on_root = 1
