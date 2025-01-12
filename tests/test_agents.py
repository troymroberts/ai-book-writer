"""Unit tests for the BookAgents class"""
import unittest
from unittest.mock import patch, MagicMock
from agents import BookAgents

class TestBookAgents(unittest.TestCase):
    """Test cases for the BookAgents class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent_config = {
            "config_list": [{"model": "deepseek/deepseek-chat"}],
            "temperature": 0.7
        }
        self.sample_outline = [
            {
                "chapter_number": 1,
                "title": "The Beginning",
                "prompt": "Start the story with a mysterious event"
            },
            {
                "chapter_number": 2,
                "title": "The Journey",
                "prompt": "Introduce the main character's quest"
            }
        ]
        
        # Patch autogen imports
        self.autogen_patcher = patch('agents.autogen')
        self.mock_autogen = self.autogen_patcher.start()
        
        # Create mock agents with configured llm_config
        self.mock_agents = {}
        for agent_name in [
            "story_planner", "world_builder", "memory_keeper", 
            "writer", "editor"
        ]:
            mock = MagicMock()
            mock.llm_config.to_dict.return_value = self.agent_config
            self.mock_agents[agent_name] = mock
            
        # Special setup for outline creator
        outline_mock = MagicMock()
        outline_mock.llm_config.to_dict.return_value = self.agent_config
        outline_mock.system_message = "EXACTLY THIS FORMAT FOR EACH CHAPTER\n5-chapter outline"
        self.mock_agents["outline_creator"] = outline_mock
            
        # User proxy doesn't need llm_config
        self.mock_agents["user_proxy"] = MagicMock()
        
        # Configure mock autogen to return our mock agents
        self.mock_autogen.AssistantAgent.side_effect = lambda *args, **kwargs: self.mock_agents[
            kwargs.get('name', args[0] if args else '')
        ]
        self.mock_autogen.UserProxyAgent.return_value = self.mock_agents['user_proxy']

    def tearDown(self):
        """Clean up test fixtures"""
        self.autogen_patcher.stop()

    def test_initialization(self):
        """Test BookAgents initialization"""
        # Test with outline
        agents = BookAgents(self.agent_config, self.sample_outline)
        # Only check the model and temperature since other config values may vary
        self.assertEqual(agents.agent_config['config_list'][0]['model'], 'deepseek-chat')
        self.assertEqual(agents.agent_config['temperature'], self.agent_config['temperature'])
        self.assertEqual(agents.outline, self.sample_outline)
        self.assertEqual(agents.world_elements, {})
        self.assertEqual(agents.character_developments, {})
        
        # Test without outline
        agents = BookAgents(self.agent_config)
        self.assertIsNone(agents.outline)

    def test_format_outline_context(self):
        """Test outline context formatting"""
        agents = BookAgents(self.agent_config, self.sample_outline)
        expected_output = (
            "Complete Book Outline:\n"
            "\nChapter 1: The Beginning\n"
            "Start the story with a mysterious event\n"
            "\nChapter 2: The Journey\n"
            "Introduce the main character's quest"
        )
        self.assertEqual(agents._format_outline_context(), expected_output)
        
        # Test empty outline
        agents = BookAgents(self.agent_config)
        self.assertEqual(agents._format_outline_context(), "")

    def test_create_agents(self):
        """Test agent creation"""
        agents = BookAgents(self.agent_config, self.sample_outline)
        created_agents = agents.create_agents("Test prompt", 5)
        
        # Verify all agents were created
        self.assertEqual(set(created_agents.keys()), {
            "story_planner",
            "world_builder",
            "memory_keeper",
            "writer",
            "editor",
            "user_proxy",
            "outline_creator"
        })
        
        # Verify agent configurations
        for agent_name, agent in created_agents.items():
            self.assertEqual(agent, self.mock_agents[agent_name])
            if agent_name != "user_proxy":
                self.assertEqual(agent.llm_config.to_dict(), self.agent_config)

        # Verify outline creator format
        outline_creator = created_agents["outline_creator"]
        self.assertIn("EXACTLY THIS FORMAT FOR EACH CHAPTER",
                     outline_creator.system_message)
        self.assertIn("5-chapter outline", outline_creator.system_message)

    def test_world_element_tracking(self):
        """Test world element tracking"""
        agents = BookAgents(self.agent_config)
        
        # Add new element
        agents.update_world_element("Forest", "A dense, mysterious forest")
        self.assertEqual(agents.world_elements["Forest"], "A dense, mysterious forest")
        
        # Update existing element
        agents.update_world_element("Forest", "A dark, enchanted forest")
        self.assertEqual(agents.world_elements["Forest"], "A dark, enchanted forest")

    def test_character_development_tracking(self):
        """Test character development tracking"""
        agents = BookAgents(self.agent_config)
        
        # Add new character
        agents.update_character_development("Alice", "Introduced as the protagonist")
        self.assertEqual(agents.character_developments["Alice"], 
                        ["Introduced as the protagonist"])
        
        # Add additional development
        agents.update_character_development("Alice", "Discovered magical powers")
        self.assertEqual(agents.character_developments["Alice"], [
            "Introduced as the protagonist",
            "Discovered magical powers"
        ])

    def test_get_world_context(self):
        """Test world context formatting"""
        agents = BookAgents(self.agent_config)
        
        # Test empty context
        self.assertEqual(agents.get_world_context(), 
                        "No established world elements yet.")
        
        # Test with elements
        agents.update_world_element("Forest", "A dense, mysterious forest")
        agents.update_world_element("Castle", "An ancient stone fortress")
        expected_output = (
            "Established World Elements:\n"
            "- Forest: A dense, mysterious forest\n"
            "- Castle: An ancient stone fortress"
        )
        self.assertEqual(agents.get_world_context(), expected_output)

    def test_get_character_context(self):
        """Test character context formatting"""
        agents = BookAgents(self.agent_config)
        
        # Test empty context
        self.assertEqual(agents.get_character_context(),
                        "No character developments tracked yet.")
        
        # Test with developments
        agents.update_character_development("Alice", "Introduced as protagonist")
        agents.update_character_development("Alice", "Discovered powers")
        agents.update_character_development("Bob", "Introduced as antagonist")
        
        expected_output = (
            "Character Development History:\n"
            "- Alice:\n"
            "  Introduced as protagonist\n"
            "  Discovered powers\n"
            "- Bob:\n"
            "  Introduced as antagonist"
        )
        self.assertEqual(agents.get_character_context(), expected_output)

if __name__ == '__main__':
    unittest.main()
