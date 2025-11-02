#!/usr/bin/env python3
"""
Octopus API - End-to-End Demo Script

This script demonstrates the complete workflow of the Octopus API.
Run with: python examples/demo.py
"""

import sys
import time
from typing import Optional

import httpx


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_section(text: str) -> None:
    """Print a section header"""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")


def print_step(text: str) -> None:
    """Print a step description"""
    print(f"{Colors.YELLOW}→ {text}{Colors.END}")


def print_success(text: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print an info message"""
    print(f"  {text}")


def wait_for_user() -> None:
    """Wait for user to press Enter"""
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.END}")


class OctopusDemo:
    """Demo script for Octopus API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
        self.client = httpx.Client(timeout=30.0)
        self.api_key: Optional[str] = None
        
        # Track created resources
        self.resources = {
            "api_keys": {},
            "users": {},
            "conversations": {}
        }
    
    def welcome(self) -> None:
        """Display welcome message"""
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BLUE}║{'Octopus API - End-to-End Demo':^58}║{Colors.END}")
        print(f"{Colors.BLUE}║{'Demonstrating Complete Workflow':^58}║{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")
    
    def check_health(self) -> bool:
        """Check if server is running"""
        print_section("1. Health Check")
        print_step("Checking if server is running...")
        
        try:
            response = self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            print_success(f"Server is running at {self.base_url}")
            return True
        except Exception as e:
            print_error("Server is not running!")
            print_info("Please start the server first:")
            print_info("  uv run fastapi dev app/main.py")
            return False
    
    def bootstrap(self) -> bool:
        """Create master API key"""
        print_section("2. Bootstrap - Create Master API Key")
        print_step("Calling bootstrap endpoint...")
        
        try:
            response = self.client.post(f"{self.base_url}/bootstrap")
            response.raise_for_status()
            data = response.json()
            
            self.api_key = data["api_key"]
            print_success("Master API key created!")
            print(f"{Colors.GREEN}API Key: {Colors.YELLOW}{self.api_key}{Colors.END}")
            print(f"\n{Colors.CYAN}💡 Save this key to your .env file:{Colors.END}")
            print(f"   MASTER_API_KEY={self.api_key}")
            return True
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                print_error("Bootstrap already completed")
                self.api_key = input("Please provide your existing master API key: ").strip()
                if not self.api_key:
                    print_error("No API key provided. Exiting.")
                    return False
                return True
            else:
                print_error(f"Bootstrap failed: {e}")
                return False
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return False
    
    def create_api_keys(self) -> None:
        """Create additional API keys"""
        print_section("3. Create Additional API Keys")
        
        headers = {"Octopus-API-Key": self.api_key}
        
        # Create read-only key
        print_step("Creating read-only API key...")
        try:
            response = self.client.post(
                f"{self.api_v1}/api-keys/",
                headers=headers,
                json={
                    "name": "Read-Only Key",
                    "description": "Key with read-only access",
                    "scopes": "read"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.resources["api_keys"]["read"] = data["key"]
            print_success(f"Read-only key created: {data['key'][:20]}...")
        except Exception as e:
            print_error(f"Failed to create read-only key: {e}")
        
        # Create read-write key
        print_step("Creating read-write API key...")
        try:
            response = self.client.post(
                f"{self.api_v1}/api-keys/",
                headers=headers,
                json={
                    "name": "Read-Write Key",
                    "description": "Key for development",
                    "scopes": "read,write"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.resources["api_keys"]["readwrite"] = data["key"]
            print_success(f"Read-write key created: {data['key'][:20]}...")
        except Exception as e:
            print_error(f"Failed to create read-write key: {e}")
        
        # List all keys
        print_step("Listing all API keys...")
        try:
            response = self.client.get(f"{self.api_v1}/api-keys/", headers=headers)
            response.raise_for_status()
            keys = response.json()
            for key in keys:
                print_info(f"- {key['name']} (ID: {key['id']})")
            print_success("API keys listed successfully")
        except Exception as e:
            print_error(f"Failed to list API keys: {e}")
    
    def create_users(self) -> None:
        """Create test users"""
        print_section("4. Create Users")
        
        headers = {"Octopus-API-Key": self.api_key}
        users = [
            {"name": "Alice", "email": "alice@example.com", "username": "alice", "full_name": "Alice Smith"},
            {"name": "Bob", "email": "bob@example.com", "username": "bob", "full_name": "Bob Jones"},
            {"name": "Charlie", "email": "charlie@example.com", "username": "charlie", "full_name": "Charlie Brown"}
        ]
        
        for user in users:
            print_step(f"Creating user: {user['name']}...")
            try:
                response = self.client.post(
                    f"{self.api_v1}/users/",
                    headers=headers,
                    json={
                        "email": user["email"],
                        "username": user["username"],
                        "password": "SecurePass123!",
                        "full_name": user["full_name"]
                    }
                )
                response.raise_for_status()
                data = response.json()
                self.resources["users"][user["name"]] = data["id"]
                print_success(f"{user['name']} created (ID: {data['id']})")
            except Exception as e:
                print_error(f"Failed to create {user['name']}: {e}")
        
        # List all users
        print_step("Listing all users...")
        try:
            response = self.client.get(f"{self.api_v1}/users/", headers=headers)
            response.raise_for_status()
            users_list = response.json()
            print_success(f"Found {len(users_list)} users in the system")
        except Exception as e:
            print_error(f"Failed to list users: {e}")
    
    def create_conversations(self) -> None:
        """Create conversations"""
        print_section("5. Create Conversations")
        
        headers = {"Octopus-API-Key": self.api_key}
        
        # Create private conversation
        print_step("Creating conversation: Alice & Bob...")
        try:
            response = self.client.post(
                f"{self.api_v1}/conversations/",
                headers=headers,
                json={
                    "title": "Alice and Bob Private Chat",
                    "participant_ids": [
                        self.resources["users"]["Alice"],
                        self.resources["users"]["Bob"]
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            self.resources["conversations"]["private"] = data["id"]
            print_success(f"Conversation created (ID: {data['id']})")
        except Exception as e:
            print_error(f"Failed to create conversation: {e}")
        
        # Create group conversation
        print_step("Creating group conversation: All Three Users...")
        try:
            response = self.client.post(
                f"{self.api_v1}/conversations/",
                headers=headers,
                json={
                    "title": "Team Discussion",
                    "participant_ids": [
                        self.resources["users"]["Alice"],
                        self.resources["users"]["Bob"],
                        self.resources["users"]["Charlie"]
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            self.resources["conversations"]["group"] = data["id"]
            print_success(f"Group conversation created (ID: {data['id']})")
        except Exception as e:
            print_error(f"Failed to create group conversation: {e}")
    
    def send_messages(self) -> None:
        """Send messages to conversations"""
        print_section("6. Add Messages to Conversations")
        
        headers = {"Octopus-API-Key": self.api_key}
        conv_id = self.resources["conversations"]["private"]
        
        messages = [
            (self.resources["users"]["Alice"], "Hi Bob! How are you?"),
            (self.resources["users"]["Bob"], "Hi Alice! I'm doing great, thanks for asking!"),
            (self.resources["users"]["Alice"], "That's great! Want to grab coffee later?")
        ]
        
        for user_id, content in messages:
            sender = [k for k, v in self.resources["users"].items() if v == user_id][0]
            print_step(f"{sender} sends message...")
            try:
                response = self.client.post(
                    f"{self.api_v1}/conversations/{conv_id}/messages",
                    headers=headers,
                    json={
                        "role": "user",
                        "content": content,
                        "user_id": user_id
                    }
                )
                response.raise_for_status()
                print_success("Message sent")
            except Exception as e:
                print_error(f"Failed to send message: {e}")
        
        # Group messages
        print_step("Adding messages to group chat...")
        group_conv_id = self.resources["conversations"]["group"]
        group_messages = [
            (self.resources["users"]["Alice"], "Hey team! Let's discuss the new project."),
            (self.resources["users"]["Bob"], "Sounds good! I have some ideas to share."),
            (self.resources["users"]["Charlie"], "Count me in! When should we start?")
        ]
        
        sent_count = 0
        for user_id, content in group_messages:
            try:
                response = self.client.post(
                    f"{self.api_v1}/conversations/{group_conv_id}/messages",
                    headers=headers,
                    json={
                        "role": "user",
                        "content": content,
                        "user_id": user_id
                    }
                )
                response.raise_for_status()
                sent_count += 1
            except Exception as e:
                print_error(f"Failed to send group message: {e}")
        
        print_success(f"{sent_count} messages added to group chat")
    
    def view_conversations(self) -> None:
        """View conversations with messages"""
        print_section("7. View Conversations with Messages")
        
        headers = {"Octopus-API-Key": self.api_key}
        
        # View private conversation
        print_step("Fetching Alice & Bob conversation...")
        print(f"\n{Colors.BLUE}━━━ Conversation: Alice and Bob Private Chat ━━━{Colors.END}")
        try:
            response = self.client.get(
                f"{self.api_v1}/conversations/{self.resources['conversations']['private']}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            print_info(f"Title: {data['title']}")
            print_info(f"Participants: {len(data['participants'])}")
            print_info("Messages:")
            for msg in data["messages"]:
                sender = msg.get("user", {}).get("username", "unknown")
                print_info(f"  [{msg['role']}] {sender}: {msg['content']}")
        except Exception as e:
            print_error(f"Failed to fetch conversation: {e}")
        
        # View group conversation
        print_step("\nFetching team discussion...")
        print(f"\n{Colors.BLUE}━━━ Conversation: Team Discussion ━━━{Colors.END}")
        try:
            response = self.client.get(
                f"{self.api_v1}/conversations/{self.resources['conversations']['group']}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            print_info(f"Title: {data['title']}")
            print_info(f"Participants: {len(data['participants'])}")
            print_info("Messages:")
            for msg in data["messages"]:
                sender = msg.get("user", {}).get("username", "unknown")
                print_info(f"  [{msg['role']}] {sender}: {msg['content']}")
        except Exception as e:
            print_error(f"Failed to fetch conversation: {e}")
    
    def list_user_conversations(self) -> None:
        """List conversations for each user"""
        print_section("8. List User-Specific Conversations")
        
        headers = {"Octopus-API-Key": self.api_key}
        
        for user_name, user_id in self.resources["users"].items():
            print_step(f"Listing {user_name}'s conversations...")
            try:
                response = self.client.get(
                    f"{self.api_v1}/conversations/user/{user_id}",
                    headers=headers
                )
                response.raise_for_status()
                convs = response.json()
                print_success(f"{user_name} is in {len(convs)} conversation(s)")
            except Exception as e:
                print_error(f"Failed to list {user_name}'s conversations: {e}")
    
    def manage_participants(self) -> None:
        """Add and remove conversation participants"""
        print_section("9. Manage Conversation Participants")
        
        headers = {"Octopus-API-Key": self.api_key}
        
        # Create new user
        print_step("Creating a new user: Diana...")
        try:
            response = self.client.post(
                f"{self.api_v1}/users/",
                headers=headers,
                json={
                    "email": "diana@example.com",
                    "username": "diana",
                    "password": "SecurePass123!",
                    "full_name": "Diana Prince"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.resources["users"]["Diana"] = data["id"]
            print_success(f"Diana created (ID: {data['id']})")
        except Exception as e:
            print_error(f"Failed to create Diana: {e}")
            return
        
        # Add Diana to group conversation
        print_step("Adding Diana to team discussion...")
        try:
            response = self.client.post(
                f"{self.api_v1}/conversations/{self.resources['conversations']['group']}/participants",
                headers=headers,
                json={"user_id": self.resources["users"]["Diana"]}
            )
            response.raise_for_status()
            print_success("Diana added to conversation")
        except Exception as e:
            print_error(f"Failed to add Diana: {e}")
        
        # Verify participant count
        print_step("Verifying participant count...")
        try:
            response = self.client.get(
                f"{self.api_v1}/conversations/{self.resources['conversations']['group']}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            print_success(f"Team discussion now has {len(data['participants'])} participants")
        except Exception as e:
            print_error(f"Failed to verify participants: {e}")
        
        # Remove Charlie
        print_step("Removing Charlie from team discussion...")
        try:
            response = self.client.delete(
                f"{self.api_v1}/conversations/{self.resources['conversations']['group']}/participants/{self.resources['users']['Charlie']}",
                headers=headers
            )
            response.raise_for_status()
            print_success("Charlie removed from conversation")
        except Exception as e:
            print_error(f"Failed to remove Charlie: {e}")
    
    def update_user(self) -> None:
        """Update user information"""
        print_section("10. Update User Information")
        
        headers = {"Octopus-API-Key": self.api_key}
        alice_id = self.resources["users"]["Alice"]
        
        print_step("Updating Alice's information...")
        try:
            response = self.client.put(
                f"{self.api_v1}/users/{alice_id}",
                headers=headers,
                json={
                    "full_name": "Alice Johnson-Smith",
                    "email": "alice.johnson@example.com"
                }
            )
            response.raise_for_status()
            print_success("Alice's information updated")
        except Exception as e:
            print_error(f"Failed to update Alice: {e}")
        
        # Fetch updated user
        print_step("Fetching updated user info...")
        try:
            response = self.client.get(f"{self.api_v1}/users/{alice_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            print_info("\nUpdated User Info:")
            print_info(f"  Username: {data['username']}")
            print_info(f"  Email: {data['email']}")
            print_info(f"  Full Name: {data['full_name']}")
        except Exception as e:
            print_error(f"Failed to fetch updated user: {e}")
    
    def show_summary(self) -> None:
        """Display demo summary"""
        print_section("11. Demo Summary")
        
        print()
        print_success("Master API key created")
        print_success("Additional API keys with different scopes")
        print_success(f"{len(self.resources['users'])} users created")
        print_success(f"{len(self.resources['conversations'])} conversations created")
        print_success("Multiple messages sent")
        print_success("Participants added and removed")
        print_success("User information updated")
        print()
        
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"{Colors.CYAN}Resources Created:{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"Master API Key: {Colors.YELLOW}{self.api_key}{Colors.END}")
        
        if self.resources["api_keys"]:
            for key_type, key_value in self.resources["api_keys"].items():
                print(f"{key_type.capitalize()} Key: {Colors.YELLOW}{key_value[:30]}...{Colors.END}")
        
        print("\nUser IDs:")
        for name, user_id in self.resources["users"].items():
            print(f"  {name:10} {user_id}")
        
        print("\nConversation IDs:")
        for conv_type, conv_id in self.resources["conversations"].items():
            print(f"  {conv_type.capitalize():15} {conv_id}")
        
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BLUE}Next Steps:{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"1. Explore the API interactively: {self.base_url}/docs")
        print("2. Check the examples folder for more curl commands")
        print("3. Read the API documentation in docs/")
        print()
        print(f"{Colors.GREEN}Demo completed successfully! 🎉{Colors.END}\n")
    
    def run(self) -> None:
        """Run the complete demo"""
        self.welcome()
        
        if not self.check_health():
            return
        
        wait_for_user()
        
        if not self.bootstrap():
            return
        
        wait_for_user()
        
        self.create_api_keys()
        wait_for_user()
        
        self.create_users()
        wait_for_user()
        
        self.create_conversations()
        wait_for_user()
        
        self.send_messages()
        wait_for_user()
        
        self.view_conversations()
        wait_for_user()
        
        self.list_user_conversations()
        wait_for_user()
        
        self.manage_participants()
        wait_for_user()
        
        self.update_user()
        wait_for_user()
        
        self.show_summary()
        
        self.client.close()


def main():
    """Main entry point"""
    try:
        demo = OctopusDemo()
        demo.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
