# RouterLink Android Proguard & R8 Rules

-keepattributes *Annotation*
-keepattributes Signature
-keepattributes InnerClasses

# Retrofit & OkHttp
-dontwarn okhttp3.**
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }
-keepattributes EnclosingMethod

# Gson & Models
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keep class com.routerlink.app.data.model.** { *; }

# WireGuard Tunnel Library
-keep class com.wireguard.** { *; }
-dontwarn com.wireguard.**

# ZXing QR Code
-keep class com.google.zxing.** { *; }
-keep class com.journeyapps.barcodescanner.** { *; }
