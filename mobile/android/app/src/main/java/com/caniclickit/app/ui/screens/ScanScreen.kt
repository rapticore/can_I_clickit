package com.caniclickit.app.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ContentPaste
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MicOff
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.caniclickit.app.ui.theme.SeverityInfo

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScanScreen(
    initialText: String = "",
    isLoading: Boolean = false,
    isListening: Boolean = false,
    onScan: (String) -> Unit,
    onVoiceInput: () -> Unit,
    onStopVoice: () -> Unit,
    onBack: () -> Unit
) {
    var inputText by remember { mutableStateOf(initialText) }
    val clipboardManager = LocalClipboardManager.current

    LaunchedEffect(initialText) {
        if (initialText.isNotBlank()) inputText = initialText
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Check Something") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Paste or type what you want to check",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            OutlinedTextField(
                value = inputText,
                onValueChange = { inputText = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 120.dp),
                placeholder = {
                    Text("A link, email address, phone number, or message…")
                },
                trailingIcon = {
                    IconButton(
                        onClick = {
                            clipboardManager.getText()?.text?.let { inputText = it }
                        }
                    ) {
                        Icon(Icons.Default.ContentPaste, "Paste from clipboard")
                    }
                },
                shape = MaterialTheme.shapes.medium,
                enabled = !isLoading
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = { onScan(inputText) },
                    modifier = Modifier
                        .weight(1f)
                        .height(56.dp),
                    enabled = inputText.isNotBlank() && !isLoading,
                    shape = MaterialTheme.shapes.medium
                ) {
                    if (isLoading) {
                        LoadingIndicator()
                    } else {
                        Icon(Icons.Default.Search, null, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Check It", style = MaterialTheme.typography.labelLarge)
                    }
                }

                FilledTonalButton(
                    onClick = { if (isListening) onStopVoice() else onVoiceInput() },
                    modifier = Modifier.size(56.dp),
                    shape = MaterialTheme.shapes.medium,
                    contentPadding = PaddingValues(0.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(
                        containerColor = if (isListening)
                            MaterialTheme.colorScheme.errorContainer
                        else
                            MaterialTheme.colorScheme.secondaryContainer
                    )
                ) {
                    Icon(
                        if (isListening) Icons.Default.MicOff else Icons.Default.Mic,
                        contentDescription = if (isListening) "Stop listening" else "Voice input",
                        modifier = Modifier.size(24.dp)
                    )
                }
            }

            if (isListening) {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    "Listening… speak now",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            if (isLoading) {
                Spacer(modifier = Modifier.height(32.dp))
                Text(
                    "Checking this for you…",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
private fun LoadingIndicator() {
    val infiniteTransition = rememberInfiniteTransition(label = "loading")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "rotation"
    )
    CircularProgressIndicator(
        modifier = Modifier
            .size(20.dp)
            .rotate(rotation),
        strokeWidth = 2.dp,
        color = MaterialTheme.colorScheme.onPrimary
    )
}
