package com.caniclickit.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.caniclickit.app.models.ConfidenceLevel
import com.caniclickit.app.models.ScanResult
import com.caniclickit.app.models.ThreatLevel
import com.caniclickit.app.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VerdictScreen(
    scanResult: ScanResult,
    onFeedback: (Boolean) -> Unit,
    onBack: () -> Unit
) {
    val verdictColor = scanResult.threatLevel.toColor()
    val verdictBgColor = scanResult.threatLevel.toBgColor()
    val verdictIcon = scanResult.threatLevel.toIcon()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Result") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = verdictBgColor
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Full-width verdict header
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(verdictBgColor)
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = verdictIcon,
                    contentDescription = null,
                    modifier = Modifier.size(72.dp),
                    tint = verdictColor
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = scanResult.threatLevel.label,
                    style = MaterialTheme.typography.headlineMedium,
                    color = verdictColor,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = scanResult.plainLanguageSummary,
                    style = MaterialTheme.typography.bodyLarge,
                    color = verdictColor.copy(alpha = 0.9f),
                    textAlign = TextAlign.Center
                )
            }

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Confidence meter
                ConfidenceMeter(scanResult.confidence)

                // Consequence warning
                scanResult.consequenceWarning?.let { warning ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = SeverityMediumBg
                        ),
                        shape = MaterialTheme.shapes.medium
                    ) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Icon(
                                Icons.Default.Warning,
                                null,
                                tint = SeverityMedium,
                                modifier = Modifier.size(24.dp)
                            )
                            Column {
                                Text(
                                    "What could happen",
                                    style = MaterialTheme.typography.labelLarge,
                                    color = SeverityMedium
                                )
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    warning,
                                    style = MaterialTheme.typography.bodyMedium
                                )
                            }
                        }
                    }
                }

                // Safe action suggestion
                scanResult.safeAction?.let { action ->
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = SeveritySafeBg
                        ),
                        shape = MaterialTheme.shapes.medium
                    ) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Icon(
                                Icons.Default.Lightbulb,
                                null,
                                tint = SeveritySafe,
                                modifier = Modifier.size(24.dp)
                            )
                            Column {
                                Text(
                                    "What to do instead",
                                    style = MaterialTheme.typography.labelLarge,
                                    color = SeveritySafe
                                )
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    action,
                                    style = MaterialTheme.typography.bodyMedium
                                )
                            }
                        }
                    }
                }

                Divider(color = MaterialTheme.colorScheme.outlineVariant)

                // Feedback
                var feedbackGiven by remember { mutableStateOf<Boolean?>(null) }
                Text(
                    "Was this helpful?",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    FilterChip(
                        selected = feedbackGiven == true,
                        onClick = {
                            feedbackGiven = true
                            onFeedback(true)
                        },
                        label = { Text("Yes") },
                        leadingIcon = {
                            Icon(Icons.Default.ThumbUp, null, modifier = Modifier.size(18.dp))
                        }
                    )
                    FilterChip(
                        selected = feedbackGiven == false,
                        onClick = {
                            feedbackGiven = false
                            onFeedback(false)
                        },
                        label = { Text("No") },
                        leadingIcon = {
                            Icon(Icons.Default.ThumbDown, null, modifier = Modifier.size(18.dp))
                        }
                    )
                }

                // Disclaimer
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "This analysis is our best assessment based on available signals.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun ConfidenceMeter(confidence: ConfidenceLevel) {
    val progress = when (confidence) {
        ConfidenceLevel.HIGH -> 1f
        ConfidenceLevel.MEDIUM -> 0.66f
        ConfidenceLevel.LOW -> 0.33f
    }

    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                "Confidence",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                confidence.label,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
        LinearProgressIndicator(
            progress = { progress },
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp),
            trackColor = MaterialTheme.colorScheme.surfaceVariant,
            color = SeverityInfo
        )
    }
}

private fun ThreatLevel.toColor(): Color = when (this) {
    ThreatLevel.DANGEROUS -> SeverityCritical
    ThreatLevel.SUSPICIOUS -> SeverityMedium
    ThreatLevel.SAFE -> SeveritySafe
}

private fun ThreatLevel.toBgColor(): Color = when (this) {
    ThreatLevel.DANGEROUS -> SeverityCriticalBg
    ThreatLevel.SUSPICIOUS -> SeverityMediumBg
    ThreatLevel.SAFE -> SeveritySafeBg
}

private fun ThreatLevel.toIcon(): ImageVector = when (this) {
    ThreatLevel.DANGEROUS -> Icons.Default.Dangerous
    ThreatLevel.SUSPICIOUS -> Icons.Default.GppMaybe
    ThreatLevel.SAFE -> Icons.Default.CheckCircle
}
