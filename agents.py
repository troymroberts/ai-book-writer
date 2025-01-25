"""Define the agents used in the book generation system with improved context management and specialized roles - DEBUGGING VERSION 4 - LOGGING ORIGINAL CREATE"""
import autogen
from typing import Dict, List, Optional
from llm.factory import LLMFactory
from llm.deepseek_client import DeepSeekClient
from llm.litellm_implementations import OllamaImplementation
from config import get_config
import logging

logger = logging.getLogger(__name__)  # Ensure logger is defined if not already

class BookAgents:
    def __init__(self, agent_config: Dict, outline: Optional[List[Dict]] = None, genre_config: Optional[Dict] = None):
        """Initialize agents with book outline context and genre configuration"""
        self.agent_config = self._prepare_autogen_config(agent_config)
        self.outline = outline
        self.genre_config = genre_config or {}
        self.world_elements = {}  # Track described locations/elements
        self.character_developments = {}  # Track character arcs

    def _prepare_autogen_config(self, config: Dict) -> Dict:
        """Prepare configuration for autogen compatibility - DIRECT PATCHING ATTEMPT"""
        if hasattr(config, 'dict'):
            config = config.dict()
        llm_config = get_config()

        config_list = []

        model_lower = llm_config.get("model", "").lower()

        if "ollama" in model_lower:
            config_list.append({
                "model": llm_config.get("model"),
                "base_url": llm_config.get("base_url"),
                "api_key": llm_config.get("api_key"),
                #"model_client_cls": "OllamaImplementation", # <-- REMOVE model_client_cls from config
                "model_kwargs": {},
            })

            # Direct patching of autogen.oai.ChatCompletion.create for Ollama
            original_create = autogen.oai.ChatCompletion.create # Store original create method

            def patched_create(*args, **kwargs): # Define patched create method
                logger.debug("Patched create function called")
                logger.debug(f"Patched create args: {args}")
                logger.debug(f"Patched create kwargs: {kwargs}")
                logger.debug(f"Type of original_create: {type(original_create)}")

                if "ollama" in kwargs.get("model", "").lower(): # Check if it's an Ollama model
                    logger.debug("Ollama model detected in patched create")
                    ollama_client = OllamaImplementation(config=llm_config) # Instantiate Ollama client DIRECTLY
                    logger.debug("Calling ollama_client.create from patched_create")
                    logger.debug(f"ollama_client.create args: {args}")
                    logger.debug(f"ollama_client.create kwargs: {kwargs}")
                    result = ollama_client.create(*args, **kwargs) # Use Ollama client's create method
                    logger.debug("Returned from ollama_client.create in patched_create")
                    logger.debug(f"Result from ollama_client.create: {result}")
                    return result
                else:
                    logger.debug("Non-Ollama model in patched create - falling back to original create")
                    if 'ollama_base_url' in kwargs:
                        logger.warning("Unexpected 'ollama_base_url' in kwargs for non-Ollama model create call - about to call original_create")
                    logger.debug("Calling original_create from patched_create")
                    logger.debug(f"original_create args: {args}")
                    logger.debug(f"original_create kwargs: {kwargs}")

                    logger.debug("About to call ORIGINAL openai.ChatCompletion.create directly (within patched_create)") # ADDED: Log before calling original create
                    if 'ollama_base_url' in kwargs: # Passing kwargs but EXCLUDING 'ollama_base_url' if present - defensive
                        kwargs_for_original = {k: v for k, v in kwargs.items() if k != 'ollama_base_url'} # Create a copy without ollama_base_url
                        logger.debug(f"Calling ORIGINAL openai.ChatCompletion.create with kwargs (excluding ollama_base_url): {kwargs_for_original}") # ADDED: Log kwargs for original create
                        result = original_create(*args, **kwargs_for_original) # Call original create, excluding ollama_base_url
                    else:
                        logger.debug(f"Calling ORIGINAL openai.ChatCompletion.create with ALL kwargs: {kwargs}") # ADDED: Log kwargs for original create
                        result = original_create(*args, **kwargs) # Fallback to original for other models
                    logger.debug("Returned from ORIGINAL openai.ChatCompletion.create in patched_create") # ADDED: Log after original create call
                    logger.debug(f"Result from original_create: {result}")
                    return result

            autogen.oai.ChatCompletion.create = patched_create # <--- APPLY THE PATCH: Override create method
            logger.debug("autogen.oai.ChatCompletion.create patched successfully in _prepare_autogen_config")


        else:  # DeepSeek configuration (as before)
            config_list.append({
                "model": "deepseek-chat",
                "api_key": llm_config.get("api_key"),
                "base_url": llm_config.get("base_url"),
                "model_client_cls": "DeepSeekClient",
                "model_kwargs": {},
            })

        return {
            **config,
            "config_list": config_list,
            # "model_client_cls": DeepSeekClient, # <-- REMOVE model_client_cls from top-level config too
        }

    def _get_genre_style_instructions(self) -> str:
        """Generate style instructions based on genre configuration"""
        if not self.genre_config:
            return ""

        style_elements = []

        if style := self.genre_config.get('WRITING_STYLE'):
            style_elements.append(f"Use {style} writing style")

        if narrative := self.genre_config.get('NARRATIVE_STYLE'):
            style_elements.append(f"Write in {narrative} perspective")

        if pacing := self.genre_config.get('PACING_SPEED'):
            pace_desc = "slower" if float(pacing) < 0.5 else "faster"
            style_elements.append(f"Maintain {pace_desc} pacing")

        if depth := self.genre_config.get('DESCRIPTIVE_DEPTH'):
            depth_desc = "detailed" if float(depth) > 0.7 else "concise"
            style_elements.append(f"Use {depth_desc} descriptions")

        for key, value in self.genre_config.items():
            if key.endswith('_DEPTH') and key not in ['DESCRIPTIVE_DEPTH']:
                feature = key.replace('_DEPTH', '').lower().replace('_', ' ')
                if float(value) > 0.7:
                    style_elements.append(f"Emphasize {feature}")

        return "\n".join([
            "\nGenre-Specific Style Instructions:",
            *[f"- {element}" for element in style_elements]
        ])

    def _format_outline_context(self) -> str:
        """Format the book outline into a readable context"""
        if not self.outline:
            return ""

        context_parts = ["Complete Book Outline:"]
        for chapter in self.outline:
            context_parts.extend([
                f"\nChapter {chapter['chapter_number']}: {chapter['title']}",
                chapter['prompt']
            ])
        return "\n".join(context_parts)

    def create_agents(self, initial_prompt, num_chapters) -> Dict:
        """Create and return all agents needed for book generation with specialized roles"""
        outline_context = self._format_outline_context()

        logger.debug("Entering BookAgents.create_agents") # ADDED: Log entry to create_agents
        logger.debug(f"Initial prompt: {initial_prompt}") # ADDED: Log initial_prompt
        logger.debug(f"Number of chapters: {num_chapters}") # ADDED: Log num_chapters
        logger.debug(f"Agent config: {self.agent_config}") # ADDED: Log agent_config

        # Memory Keeper: Maintains story continuity and context
        memory_keeper = autogen.AssistantAgent(
            name="memory_keeper",
            system_message=f"""You are the keeper of the story's continuity and context.
            Your responsibilities:
            1. Track and summarize each chapter's key events, character developments, and world details.
            2. Monitor character development and relationships for consistency.
            3. Maintain world-building consistency and established lore.
            4. Flag any continuity issues or inconsistencies to the Writer and Editor.

            Book Overview:
            {outline_context}

            Format your responses as follows, starting each update with its category tag:
            - MEMORY UPDATE: [General summary of chapter context]
            - EVENT: [List key events with brief descriptions]
            - CHARACTER: [List character developments and arc progression]
            - WORLD: [List new or updated world details and setting elements]
            - CONTINUITY ALERT: [Flag any continuity problems or inconsistencies]

            Be concise and focus on the most important information for maintaining story coherence.
            """,
            llm_config=self.agent_config,
        )
        if memory_keeper is None:
            logger.error("Failed to create memory_keeper agent.")
            return None
        logger.debug("Created memory_keeper agent") # ADDED: Log after creation

        # Story Planner - Focuses on high-level story structure
        story_planner = autogen.AssistantAgent(
            name="story_planner",
            system_message=f"""You are an expert story arc planner focused on overall narrative structure and pacing.

            Your sole responsibility is creating and refining the high-level story arc and ensuring effective pacing across the book.
            When given an initial story premise and outline:
            1. Identify major plot points, story beats, and turning points.
            2. Map character arcs and development across the entire narrative.
            3. Plan narrative pacing for each section of the book to control tension and reader engagement.
            4. Ensure a compelling overall story structure with a clear beginning, rising action, climax, falling action, and resolution (or appropriate open ending if genre-specific).
            5. Review chapter outlines to ensure they contribute effectively to the overall story arc and pacing.

            Format your output EXACTLY as:
            STORY_ARC_PLAN:
            - Overall Story Arc:
            [Describe the major phases of the story: Setup, Rising Action, Climax, Falling Action, Resolution]

            - Major Plot Points:
            [List each major event that drives the story forward in sequence]

            - Character Arc Overview:
            [For each main character, describe their intended development path across the book]

            - Pacing Plan:
            [Describe the intended pacing for different sections of the book, noting where pacing should be faster or slower to maximize impact]

            - Chapter Outline Review:
            [Provide feedback on the chapter outlines in terms of how well they fit into the planned story arc and pacing. Suggest any adjustments needed to strengthen the overall narrative]

            Always provide specific, detailed content - never use placeholders. Focus on actionable feedback to improve story structure and pacing.""",
            llm_config=self.agent_config,
        )
        if story_planner is None:
            logger.error("Failed to create story_planner agent.")
            return None
        logger.debug("Created story_planner agent") # ADDED: Log after creation


        # Outline Creator - Creates detailed chapter outlines
        outline_creator = autogen.AssistantAgent(
            name="outline_creator",
            system_message=f"""You are an expert outline creator who generates detailed chapter outlines based on story premises and story arc plans.

            Generate a detailed {num_chapters}-chapter outline following a strict format.

            YOU MUST USE EXACTLY THIS FORMAT FOR EACH CHAPTER - NO DEVIATIONS:

            Chapter [CHAPTER NUMBER]: [Chapter Title]
            Chapter Title: [Same title as above]
            Key Events:
            - [Specific Event 1]
            - [Specific Event 2]
            - [Specific Event 3]
            Character Developments: [Specific character moments and changes in this chapter]
            Setting: [Specific location and atmosphere for this chapter]
            Tone: [Specific emotional and narrative tone for this chapter]

            [REPEAT THIS EXACT FORMAT FOR ALL {num_chapters} CHAPTERS]

            Requirements:
            1. EVERY field (Chapter Title, Key Events, Character Developments, Setting, Tone) must be present for EVERY chapter.
            2. EVERY chapter must have AT LEAST 3 specific Key Events, clearly described.
            3. ALL chapters must be detailed and specific - absolutely no placeholders or vague descriptions.
            4. Format must match EXACTLY - including all headings, bullet points, and spacing.
            5. Ensure chapter titles are engaging and descriptive.
            6. Key Events should be action-oriented and drive the plot forward.
            7. Character Developments should show clear progression or change in characters.
            8. Setting descriptions should be vivid and contribute to the chapter's atmosphere.
            9. Tone should be clearly defined and set the emotional and narrative mood for this chapter.

            Initial Premise:
            {initial_prompt}

            Story Arc Plan (from Story Planner):
            [To be provided by Story Planner - wait for input]

            WORLD ELEMENTS (from World Builder):
            [To be provided by World Builder - wait for input]

            START WITH 'OUTLINE:' and clearly separate each chapter. END WITH 'END OF OUTLINE'.
            """,
            llm_config=self.agent_config,
        )
        if outline_creator is None:
            logger.error("Failed to create outline_creator agent.")
            return None
        logger.debug("Created outline_creator agent") # ADDED: Log after creation

        # Setting Builder: Creates and maintains the story setting (Renamed and enhanced World Builder)
        setting_builder = autogen.AssistantAgent(
            name="setting_builder",
            system_message=f"""You are an expert in setting and world-building, responsible for creating rich, consistent, and evolving settings that enhance the story.

            Your role is to establish ALL settings and world elements needed for the entire story and ensure they are dynamically integrated as the story progresses.

            Book Overview:
            {outline_context}

            Your responsibilities:
            1. Review the story arc and outline to identify every location and setting needed for each chapter.
            2. Create detailed descriptions for each setting, including:
            - Physical layout and sensory details (sights, sounds, smells, textures).
            - Atmosphere, mood, and environmental conditions (time of day, weather, lighting).
            - Key objects, features, and points of interest within each setting.
            - Emotional and thematic resonance of each setting in relation to the story.
            3. Identify recurring locations and plan how they evolve or change over time to reflect story progression and character development.
            4. Establish clear connections and transitions between different settings, considering character movement and spatial relationships.
            5. Ensure all settings are cohesive and contribute to the overall world-building and story themes.

            Format your response as:
            SETTING_DETAILS:

            [LOCATION NAME - Chapter Number(s)]:
            - Physical Description: [detailed description including sensory details]
            - Atmosphere and Mood: [mood, time of day, lighting, weather, etc.]
            - Key Features: [important objects, layout elements, points of interest]
            - Thematic Resonance: [how this setting enhances story themes and character emotions]

            [RECURRING SETTINGS - Locations Appearing Multiple Times]:
            - [LOCATION NAME]: [Description of how this setting evolves across chapters, noting changes and recurring elements]

            [SETTING TRANSITIONS - Connections Between Locations]:
            - [LOCATION 1] to [LOCATION 2]: [Describe how characters move between these settings and any significant spatial relationships or transitions]

            Ensure every setting is vividly described and contributes meaningfully to the narrative.
            """,
            llm_config=self.agent_config,
        )
        if setting_builder is None:
            logger.error("Failed to create setting_builder agent.")
            return None
        logger.debug("Created setting_builder agent") # ADDED: Log after creation

        # Character Agent: Develops and maintains character details (New Agent)
        character_agent = autogen.AssistantAgent(
            name="character_agent",
            system_message=f"""You are the character development expert, responsible for creating and maintaining consistent, engaging, and evolving characters throughout the book.

            Your role is to define and track all key characters, ensuring depth, consistency, and compelling arcs.

            Book Overview:
            {outline_context}

            Your responsibilities:
            1. Develop detailed character profiles for all main and significant supporting characters based on the story premise and outline.
            2. Define character backstories, motivations, personalities, strengths, weaknesses, and relationships.
            3. Track character arcs across the entire narrative, ensuring logical progression and impactful transformations.
            4. Maintain consistency in character voice, behavior, and development throughout the book.
            5. Ensure character actions and decisions are motivated and believable within the story context.

            Format your response as:
            CHARACTER_PROFILES:

            [CHARACTER NAME]:
            - Backstory: [Detailed backstory relevant to their current role in the story]
            - Motivations: [Primary and secondary motivations driving their actions]
            - Personality: [Key personality traits, including strengths and weaknesses]
            - Relationships: [Significant relationships with other characters, noting dynamics]
            - Arc Overview: [Intended character arc across the story - how will they change and develop?]

            [CHARACTER ARCS - Detailed Chapter Breakdown]:
            - [CHARACTER NAME] - Chapter [CHAPTER NUMBER]: [Describe specific character developments, actions, and emotional states within this chapter, linking to their overall arc]

            Ensure each character is richly developed and their journey is compelling and consistent.
            """,
            llm_config=self.agent_config,
        )
        if character_agent is None:
            logger.error("Failed to create character_agent agent.")
            return None
        logger.debug("Created character_agent agent") # ADDED: Log after creation

        # Plot Agent: Focuses on plot details and pacing within chapters (New Agent)
        plot_agent = autogen.AssistantAgent(
            name="plot_agent",
            system_message=f"""You are the plot detail expert, responsible for ensuring each chapter's plot is engaging, well-paced, and contributes to the overall story arc.

            Your role is to refine chapter outlines to maximize plot effectiveness and pacing at the chapter level.

            Book Overview:
            {outline_context}

            Your responsibilities:
            1. Review chapter outlines to ensure each chapter has a compelling plot progression with clear rising action, climax, and resolution (within the chapter context).
            2. Refine 'Key Events' in chapter outlines to be specific, impactful, and logically sequenced to drive the plot forward.
            3. Suggest pacing adjustments for each chapter to control tension, suspense, and reader engagement effectively.
            4. Ensure subplots (if any) are well-integrated within chapter plots and contribute to the main story arc.
            5. Identify and resolve any plot holes, inconsistencies, or pacing issues within chapter outlines.

            Format your response as:
            CHAPTER_PLOT_ANALYSIS:

            [Chapter Number]: [Chapter Title] - Plot and Pacing Analysis:
            - Plot Summary & Progression: [Summarize the chapter plot and assess its progression and engagement]
            - Key Event Refinements: [Suggest specific improvements or additions to 'Key Events' to enhance plot impact and clarity]
            - Pacing Suggestions: [Recommend pacing adjustments for the chapter - where to speed up, slow down, build tension, etc.]
            - Subplot Integration (if applicable): [Analyze how subplots are integrated and suggest improvements for clarity and impact]
            - Plot Issue Identification: [Point out any plot holes, inconsistencies, or pacing problems and suggest solutions]

            Provide detailed, actionable feedback to strengthen chapter plots and pacing, ensuring each chapter is a compelling part of the overall narrative.
            """,
            llm_config=self.agent_config,
        )
        if plot_agent is None:
            logger.error("Failed to create plot_agent agent.")
            return None
        logger.debug("Created plot_agent agent") # ADDED: Log after creation

        # Writer: Generates the actual prose
        writer_message = f"""You are an expert creative writer who brings scenes to life with vivid prose, compelling characters, and engaging plots.

        Book Context:
        {outline_context}

        Established World Elements:
        {self.get_world_context()}

        Character Development History:
        {self.get_character_context()}

        Your focus for each chapter:
            1. Write according to the detailed chapter outline, incorporating all Key Events, Character Developments, Setting, and Tone.
            2. Maintain consistent character voices and personalities as defined by the Character Agent.
            3. Vividly incorporate world-building details and settings as established by the Setting Builder.
            4. Create engaging and immersive prose that captures the intended tone and style for the genre and chapter.
            5. Ensure each chapter is a complete and satisfying scene with a clear beginning, middle, and end - do not leave scenes incomplete or abruptly cut off.
            6. Each chapter MUST be at least 5000 words (approximately 30,000 characters). Consider this a hard requirement. If your output is shorter, continue writing until you reach this minimum length.
            7. Ensure smooth and logical transitions between paragraphs and scenes within the chapter.
            8. Add rich sensory details and descriptions of the environment and characters where appropriate to enhance immersion and engagement.

        Always reference the chapter outline, previous chapter content (as summarized by the Memory Keeper), established world elements, and character developments to ensure consistency and coherence.

        Mark initial drafts with 'SCENE DRAFT:' and final, revised versions with 'SCENE FINAL:'.

        {self._get_genre_style_instructions()}"""

        writer = autogen.AssistantAgent(
            name="writer",
            system_message=writer_message,
            llm_config=self.agent_config,
        )
        if writer is None:
            logger.error("Failed to create writer agent.")
            return None
        logger.debug("Created writer agent") # ADDED: Log after creation

        # Editor: Reviews and improves content
        editor = autogen.AssistantAgent(
            name="editor",
            system_message=f"""You are an expert editor ensuring quality, consistency, and adherence to the book outline and style guidelines.

            Book Overview:
            {outline_context}

            Established World Elements:
            {self.get_world_context()}

            Character Development History:
            {self.get_character_context()}


            Your focus for each chapter:
            1. Check for strict alignment with the chapter outline - verify all Key Events, Character Developments, Setting, and Tone are incorporated accurately.
            2. Verify character consistency with established character profiles and previous chapters.
            3. Maintain world-building rules and consistency with established world elements.
            4. Critically review and improve prose quality - enhance clarity, flow, pacing, sentence structure, vocabulary, and descriptive language.
            5. Ensure each chapter is a complete and satisfying scene with a clear beginning, middle, and end.
            6. Verify each chapter meets the minimum word count of 5000 words. If shorter, return it to the Writer for expansion, specifying areas needing more detail or development. This is a hard requirement - do not approve chapters shorter than 5000 words.
            7. Check for smooth transitions between paragraphs and scenes and suggest improvements.

            Format your responses as follows:
            1. Start critiques with 'FEEDBACK:' - provide specific feedback on areas needing improvement, referencing outline elements and style guidelines.
            2. Provide direct suggestions with 'SUGGESTION:' - offer concrete suggestions for revisions and improvements.
            3. Return the full edited chapter with 'EDITED_SCENE:' - clearly mark the final edited chapter content.

            Reference specific outline elements, style guidelines, and previous chapter feedback in your critiques and suggestions. Do not proceed to the next chapter until the current chapter is finalized and meets all quality and length requirements. Never ask to start the next chapter, as the next step is finalizing the current chapter.""",
            llm_config=self.agent_config,
        )
        if editor is None:
            logger.error("Failed to create editor agent.")
            return None
        logger.debug("Created editor agent") # ADDED: Log after creation

        # User Proxy: Manages the interaction
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="TERMINATE",
            code_execution_config=False,  # Removed code execution capability
            max_consecutive_auto_reply=10  # Increased auto-reply limit if needed
        )
        if user_proxy is None:
            logger.error("Failed to create user_proxy agent.")
            return None
        logger.debug("Created user_proxy agent") # ADDED: Log after creation

        agent_list = [memory_keeper, story_planner, outline_creator, setting_builder, character_agent, plot_agent, writer, editor, user_proxy]  # List of agents

        llm_config = get_config()  # Get config again to access model info

        model_lower = llm_config.get("model", "").lower()  # Get model name again

        # Dynamically register model client based on LLM_MODEL
        if "ollama" in model_lower:
            model_client_cls = OllamaImplementation  # Use Ollama client for Ollama models
        else:
            model_client_cls = DeepSeekClient  # Default to DeepSeek for other models (or adjust as needed)

        logger.debug(f"LLM Model class to be registered: {model_client_cls}") # ADDED: Log model client class

        for agent in agent_list:
            if isinstance(agent, autogen.AssistantAgent):
                model_name_to_check = llm_config.get("model", "").lower() # Get model name for check
                if "ollama" not in model_name_to_check: # Conditionally register client - skip for ollama
                    print(f"Registering model client for agent: {agent.name if hasattr(agent, 'name') else agent.__class__.__name__}")
                    agent.register_model_client(model_client_cls=model_client_cls)
                else:
                    print(f"Skipping model client registration for Ollama agent: {agent.name if hasattr(agent, 'name') else agent.__class__.__name__} - using direct patching") # Log skip for Ollama
                    print(f"Skipping register_model_client for {agent.name if hasattr(agent, 'name') else agent.__class__.__name__} as it is not an AssistantAgent")
            logger.debug(f"Agent {agent.name if hasattr(agent, 'name') else agent.__class__.__name__} llm_config after registration: {agent.llm_config}") # ADDED: Log agent llm_config after registration

        logger.debug("Exiting BookAgents.create_agents and returning agents dict") # ADDED: Log exit of create_agents
        return {
            "story_planner": story_planner,
            "setting_builder": setting_builder,  # Renamed and using setting_builder now
            "character_agent": character_agent,  # Added character_agent
            "plot_agent": plot_agent,  # Added plot_agent
            "memory_keeper": memory_keeper,
            "writer": writer,
            "editor": editor,
            "user_proxy": user_proxy,
            "outline_creator": outline_creator
        }

    def update_world_element(self, element_name: str, description: str) -> None:
        """Track a new or updated world element"""
        self.world_elements[element_name] = description

    def update_character_development(self, character_name: str, development: str) -> None:
        """Track character development"""
        if character_name not in self.character_developments:
            self.character_developments[character_name] = []
        self.character_developments[character_name].append(development)

    def get_world_context(self) -> str:
        """Get formatted world-building context"""
        if not self.world_elements:
            return "No established world elements yet."

        return "\n".join([
            "Established World Elements:",
            *[f"- {name}: {desc}" for name, desc in self.world_elements.items()]
        ])

    def get_character_context(self) -> str:
        """Get formatted character development context"""
        if not self.character_developments:
            return "No character developments tracked yet."

        return "\n".join([
            "Character Development History:",
            *[f"- {name}:\n  " + "\n  ".join(devs)
              for name, devs in self.character_developments.items()]
        ])