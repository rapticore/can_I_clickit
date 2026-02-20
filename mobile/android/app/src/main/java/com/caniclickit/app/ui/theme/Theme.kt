package com.caniclickit.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat

// --- Neutral palette ---
val Neutral0 = Color(0xFFFFFFFF)
val Neutral50 = Color(0xFFF9FAFB)
val Neutral100 = Color(0xFFF2F4F7)
val Neutral200 = Color(0xFFEAECF0)
val Neutral300 = Color(0xFFD0D5DD)
val Neutral400 = Color(0xFF98A2B3)
val Neutral500 = Color(0xFF667085)
val Neutral600 = Color(0xFF475467)
val Neutral700 = Color(0xFF344054)
val Neutral800 = Color(0xFF1D2939)
val Neutral900 = Color(0xFF101828)

// --- Severity colors ---
val SeverityCritical = Color(0xFFD92D20)
val SeverityHigh = Color(0xFFF04438)
val SeverityMedium = Color(0xFFF79009)
val SeveritySafe = Color(0xFF12B76A)
val SeverityInfo = Color(0xFF2E90FA)

// --- Severity background tints ---
val SeverityCriticalBg = Color(0xFFFEF3F2)
val SeverityHighBg = Color(0xFFFEF3F2)
val SeverityMediumBg = Color(0xFFFFFAEB)
val SeveritySafeBg = Color(0xFFECFDF3)
val SeverityInfoBg = Color(0xFFEFF8FF)

// --- Light color scheme ---
private val LightColorScheme = lightColorScheme(
    primary = SeverityInfo,
    onPrimary = Neutral0,
    primaryContainer = SeverityInfoBg,
    onPrimaryContainer = Color(0xFF1849A9),
    secondary = Neutral600,
    onSecondary = Neutral0,
    secondaryContainer = Neutral100,
    onSecondaryContainer = Neutral700,
    tertiary = SeveritySafe,
    onTertiary = Neutral0,
    error = SeverityCritical,
    onError = Neutral0,
    errorContainer = SeverityCriticalBg,
    onErrorContainer = Color(0xFF912018),
    background = Neutral0,
    onBackground = Neutral900,
    surface = Neutral0,
    onSurface = Neutral900,
    surfaceVariant = Neutral50,
    onSurfaceVariant = Neutral600,
    outline = Neutral300,
    outlineVariant = Neutral200
)

// --- Dark color scheme ---
private val DarkColorScheme = darkColorScheme(
    primary = SeverityInfo,
    onPrimary = Neutral0,
    primaryContainer = Color(0xFF1849A9),
    onPrimaryContainer = SeverityInfoBg,
    secondary = Neutral400,
    onSecondary = Neutral900,
    secondaryContainer = Neutral700,
    onSecondaryContainer = Neutral200,
    tertiary = SeveritySafe,
    onTertiary = Neutral0,
    error = SeverityHigh,
    onError = Neutral0,
    errorContainer = Color(0xFF55160C),
    onErrorContainer = Color(0xFFFECDCA),
    background = Neutral900,
    onBackground = Neutral100,
    surface = Neutral900,
    onSurface = Neutral100,
    surfaceVariant = Neutral800,
    onSurfaceVariant = Neutral400,
    outline = Neutral600,
    outlineVariant = Neutral700
)

val InterFontFamily = FontFamily.Default
val IbmPlexSansFontFamily = FontFamily.Default

val AppTypography = Typography(
    headlineLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 40.sp,
        letterSpacing = (-0.5).sp
    ),
    headlineMedium = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp,
        lineHeight = 36.sp,
        letterSpacing = (-0.25).sp
    ),
    headlineSmall = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 32.sp
    ),
    titleLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp
    ),
    titleMedium = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 24.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = IbmPlexSansFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = IbmPlexSansFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    bodySmall = TextStyle(
        fontFamily = IbmPlexSansFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp
    ),
    labelLarge = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
        lineHeight = 20.sp
    ),
    labelMedium = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 18.sp
    ),
    labelSmall = TextStyle(
        fontFamily = InterFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp
    )
)

val AppShapes = Shapes(
    extraSmall = RoundedCornerShape(4.dp),
    small = RoundedCornerShape(6.dp),
    medium = RoundedCornerShape(8.dp),
    large = RoundedCornerShape(12.dp),
    extraLarge = RoundedCornerShape(16.dp)
)

@Composable
fun CanIClickItTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content
    )
}
