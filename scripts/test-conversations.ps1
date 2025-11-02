# Test script for many-to-many conversations
$baseUrl = "http://localhost:8000/api/v1"
$apiKey = "your-secret-api-key-here"
$headers = @{ "Octopus-API-Key" = $apiKey }

Write-Host "`n=== Testing Many-to-Many Conversations ===" -ForegroundColor Cyan

# Helper function to create or get existing user
function Get-OrCreateUser {
    param($email, $username, $password, $fullName)
    
    try {
        # Try to create user
        $user = Invoke-RestMethod -Uri "$baseUrl/users/" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
            email = $email
            username = $username
            password = $password
            full_name = $fullName
        } | ConvertTo-Json) -ErrorAction Stop
        Write-Host "Created new user: $username (ID: $($user.id))" -ForegroundColor Green
        return $user
    } catch {
        # User exists, get by username
        try {
            $user = Invoke-RestMethod -Uri "$baseUrl/users/username/$username" -Method Get -ErrorAction Stop
            Write-Host "Using existing user: $username (ID: $($user.id))" -ForegroundColor Yellow
            return $user
        } catch {
            Write-Host "Error getting user $username" -ForegroundColor Red
            throw
        }
    }
}

# 1. Create or get users
Write-Host "`n1. Getting/Creating users..." -ForegroundColor Yellow
$user1 = Get-OrCreateUser -email "alice@example.com" -username "alice" -password "password123" -fullName "Alice Smith"
$user2 = Get-OrCreateUser -email "bob@example.com" -username "bob" -password "password123" -fullName "Bob Jones"

# 2. Create a conversation with both users
Write-Host "`n2. Creating conversation between Alice and Bob..." -ForegroundColor Yellow
$conversation = Invoke-RestMethod -Uri "$baseUrl/conversations/" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    title = "Alice and Bob's Chat"
    participant_ids = @($user1.id, $user2.id)
} | ConvertTo-Json)
Write-Host "Created conversation: $($conversation.title) (ID: $($conversation.id))" -ForegroundColor Green
Write-Host "Participants: $($conversation.participants.Count)" -ForegroundColor Green
foreach ($p in $conversation.participants) {
    Write-Host "  - $($p.username) ($($p.email))" -ForegroundColor Gray
}

# 3. Add a message to the conversation
Write-Host "`n3. Adding messages to the conversation..." -ForegroundColor Yellow
$message1 = Invoke-RestMethod -Uri "$baseUrl/conversations/$($conversation.id)/messages" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    role = "user"
    content = "Hi Bob! How are you?"
    user_id = $user1.id
} | ConvertTo-Json)
Write-Host "Message from Alice added (user_id: $($message1.user_id))" -ForegroundColor Green

$message2 = Invoke-RestMethod -Uri "$baseUrl/conversations/$($conversation.id)/messages" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    role = "user"
    content = "Hi Alice! I'm doing great, thanks!"
    user_id = $user2.id
} | ConvertTo-Json)
Write-Host "Message from Bob added (user_id: $($message2.user_id))" -ForegroundColor Green

# 4. Get the conversation with messages
Write-Host "`n4. Retrieving conversation with all messages..." -ForegroundColor Yellow
$fullConversation = Invoke-RestMethod -Uri "$baseUrl/conversations/$($conversation.id)" -Method Get -Headers $headers
Write-Host "Conversation: $($fullConversation.title)" -ForegroundColor Green
Write-Host "Messages: $($fullConversation.messages.Count)" -ForegroundColor Green
foreach ($msg in $fullConversation.messages) {
    $sender = if ($msg.user) { $msg.user.username } else { "unknown" }
    Write-Host "  [$($msg.role)] $sender`: $($msg.content)" -ForegroundColor Gray
}

# 5. Create a third user and add them to the conversation
Write-Host "`n5. Creating/Getting a third user and adding to conversation..." -ForegroundColor Yellow
$user3 = Get-OrCreateUser -email "charlie@example.com" -username "charlie" -password "password123" -fullName "Charlie Brown"

$updatedConversation = Invoke-RestMethod -Uri "$baseUrl/conversations/$($conversation.id)/participants" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    user_id = $user3.id
} | ConvertTo-Json)
Write-Host "Added Charlie to the conversation" -ForegroundColor Green
Write-Host "Participants now: $($updatedConversation.participants.Count)" -ForegroundColor Green
foreach ($p in $updatedConversation.participants) {
    Write-Host "  - $($p.username) ($($p.email))" -ForegroundColor Gray
}

# 6. List conversations for a specific user
Write-Host "`n6. Listing conversations for Alice..." -ForegroundColor Yellow
$aliceConversations = Invoke-RestMethod -Uri "$baseUrl/conversations/user/$($user1.id)" -Method Get -Headers $headers
Write-Host "Alice is in $($aliceConversations.Count) conversation(s)" -ForegroundColor Green
foreach ($conv in $aliceConversations) {
    Write-Host "  - $($conv.title) with $($conv.participants.Count) participants" -ForegroundColor Gray
}

# 7. Remove a participant
Write-Host "`n7. Removing Charlie from the conversation..." -ForegroundColor Yellow
$finalConversation = Invoke-RestMethod -Uri "$baseUrl/conversations/$($conversation.id)/participants/$($user3.id)" -Method Delete -Headers $headers
Write-Host "Removed Charlie from the conversation" -ForegroundColor Green
Write-Host "Participants now: $($finalConversation.participants.Count)" -ForegroundColor Green
foreach ($p in $finalConversation.participants) {
    Write-Host "  - $($p.username) ($($p.email))" -ForegroundColor Gray
}

Write-Host "`n=== Test Complete! ===" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  - Created 3 users" -ForegroundColor Gray
Write-Host "  - Created 1 conversation with 2 participants" -ForegroundColor Gray
Write-Host "  - Added 2 messages" -ForegroundColor Gray
Write-Host "  - Added and removed participants dynamically" -ForegroundColor Gray
Write-Host "  - Queried user-specific conversations" -ForegroundColor Gray
