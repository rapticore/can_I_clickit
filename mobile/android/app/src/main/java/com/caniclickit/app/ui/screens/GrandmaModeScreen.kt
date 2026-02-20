package com.caniclickit.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MicOff
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GrandmaModeScreen(
    isLoading: Boolean = false,
    isListening: Boolean = false,
    recognizedText: String = "",
    onScan: (String) -> Unit,
    onVoiceInput: () -> Unit,
    onStopVoice: () -> Unit,
    onBack: () -> Unit
) {
    var inputText by remember { mutableStateOf("") }
    val clipboardManager = LocalClipboardManager.current

    LaunchedEffect(recognizedText) {
        if (recognizedText.isNotBlank()) inputText = recognizedText
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Check If It's Safe",
                        style = MaterialTheme.typography.headlineSmall
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            "Back",
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 24.dp, vertical = 20.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Tap the big button and tell us what you received",
                style = MaterialTheme.typography.bodyLarge.copy(fontSize = 24.sp),
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            // Always-visible oversized microphone button (72dp+)
            Button(
                onClick = { if (isListening) onStopVoice() else onVoiceInput() },
                modifier = Modifier
                    .size(120.dp),
                shape = MaterialTheme.shapes.extraLarge,
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isListening)
                        MaterialTheme.colorScheme.error
                    else
                        MaterialTheme.colorScheme.primary
                ),
                contentPadding = PaddingValues(0.dp)
            ) {
                Icon(
                    if (isListening) Icons.Default.MicOff else Icons.Default.Mic,
                    contentDescription = if (isListening) "Stop" else "Speak",
                    modifier = Modifier.size(56.dp)
                )
            }

            if (isListening) {
                Text(
                    "Listening… speak now",
                    style = MaterialTheme.typography.bodyLarge.copy(fontSize = 24.sp),
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold
                )
            }

            if (inputText.isNotBlank()) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(min = 100.dp),
                    textStyle = MaterialTheme.typography.bodyLarge.copy(fontSize = 24.sp),
                    shape = MaterialTheme.shapes.medium,
                    enabled = !isLoading
                )
            }

            Spacer(modifier = Modifier.weight(1f))

            // Oversized check button (72dp+ height)
            Button(
                onClick = {
                    val text = inputText.ifBlank {
                        clipboardManager.getText()?.text.orEmpty()
                    }
                    if (text.isNotBlank()) onScan(text)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(80.dp),
                enabled = (inputText.isNotBlank() || clipboardManager.getText() != null) && !isLoading,
                shape = MaterialTheme.shapes.medium
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(32.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                        strokeWidth = 3.dp
                    )
                } else {
                    Icon(
                        Icons.Default.Search,
                        null,
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(Modifier.width(12.dp))
                    Text(
                        "Check If It's Safe",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}
