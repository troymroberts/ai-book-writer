"""Main class for generating books using AutoGen with improved iteration control and new agents - now with status updates for UI"""
import autogen
from typing import Dict, List, Optional
import os
import time
import re
import logging

logger = logging.getLogger(__name__)

class BookGenerator:
    def __init__(self, agents: Dict[str, autogen.ConversableAgent], agent_config: Dict, outline: List[Dict]):
        """Initialize with outline to maintain chapter count context"""
        self.agents = agents
        self.agent_config = agent_config
        self.output_dir = "book_output"
        self.chapters_memory = []  # Store chapter summaries
        self.max_iterations = 3
        self.outline = outline
        os.makedirs(self.output_dir, exist_ok=True)

    def _clean_chapter_content(self, content: str) -> str:
        """Clean up chapter content while preserving meaningful text"""
        content = re.sub(r'\(Chapter \d+.*?\)', '', content)
        content = content.replace('**', '')
        content = content.replace('__', '')
        content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
        return content

    def _generate_table_of_contents(self):
        """Generate a table of contents file from the outline"""
        toc_path = os.path.join(self.output_dir, "toc.txt")
        with open(toc_path, "w") as f:
            f.write("Table of Contents\n\n")
            for chapter in sorted(self.outline, key=lambda x: x['chapter_number']):
                f.write(f"Chapter {chapter['chapter_number']}: {chapter['title']}\n")
        logger.info(f"Generated table of contents at {toc_path}")

    def initiate_group_chat(self) -> autogen.GroupChat:
        """Create a new group chat for the agents including new specialized agents"""
        outline_context = "\n".join([
            f"\nChapter {ch['chapter_number']}: {ch['title']}\n{ch['prompt']}"
            for ch in sorted(self.outline, key=lambda x: x['chapter_number'])
        ])

        messages = [{
            "role": "system",
            "content": f"Complete Book Outline:\n{outline_context}"
        }]

        writer_final = autogen.AssistantAgent(
            name="writer_final",
            system_message=self.agents["writer"].system_message,
            llm_config=self.agent_config
        )

        return autogen.GroupChat(
            agents=[
                self.agents["user_proxy"],
                self.agents["memory_keeper"],
                self.agents["story_planner"],
                self.agents["setting_builder"],
                self.agents["character_agent"],
                self.agents["plot_agent"],
                self.agents["writer"],
                self.agents["editor"],
                writer_final
            ],
            messages=messages,
            max_round=6,
            speaker_selection_method="round_robin"
        )

    def _get_sender(self, msg: Dict) -> str:
        """Helper to get sender from message regardless of format"""
        return msg.get("sender") or msg.get("name", "")

    def _verify_chapter_complete(self, messages: List[Dict]) -> bool:
        """Verify chapter completion by analyzing entire conversation context"""
        logger.debug("Verifying chapter completion")
        current_chapter = None
        has_final_content = False
        sequence_complete = {
            'memory_update': False,
            'plan': False,  # Plan from Story Planner (optional)
            'setting': False,  # Setting from Setting Builder (optional)
            'character': False,  # Character from Character Agent (optional)
            'plot': False,  # Plot from Plot Agent (optional)
            'scene': False,
            'feedback': False,
            'scene_final': False,
            'confirmation': False
        }

        for msg in messages:
            content = msg.get("content", "")
            sender = self._get_sender(msg)

            if not current_chapter:
                num_match = re.search(r"Chapter (\d+):", content)
                if num_match:
                    current_chapter = int(num_match.group(1))

            if "MEMORY UPDATE:" in content:
                sequence_complete['memory_update'] = True
            if "PLAN:" in content:
                sequence_complete['plan'] = True  # Expecting plan tag (optional)
            if "SETTING:" in content:
                sequence_complete['setting'] = True  # Expecting setting tag (optional)
            if "CHARACTER:" in content:
                sequence_complete['character'] = True  # Expecting character tag (optional)
            if "PLOT:" in content:
                sequence_complete['plot'] = True  # Expecting plot tag (optional)
            if "SCENE DRAFT:" in content or "SCENE:" in content:
                sequence_complete['scene'] = True
            if "FEEDBACK:" in content:
                sequence_complete['feedback'] = True
            if "SCENE FINAL:" in content and sender in ["writer_final", "writer"]:
                sequence_complete['scene_final'] = True
                has_final_content = True
            if "**Confirmation:**" in content and "successfully" in content:
                sequence_complete['confirmation'] = True

            logger.debug(f"Sequence complete: {sequence_complete}")
            logger.debug(f"Current chapter: {current_chapter}")
            logger.debug(f"Has final content: {has_final_content}")

        return all(sequence_complete.values()) and current_chapter and has_final_content

    def _prepare_chapter_context(self, chapter_number: int, prompt: str) -> str:
        """Prepare context for chapter generation"""
        if chapter_number == 1:
            return f"Initial Chapter\nRequirements:\n{prompt}"

        context_parts = [
            "Previous Chapter Summaries:",
            *[f"Chapter {i+1}: {summary}" for i, summary in enumerate(self.chapters_memory)],
            "\nCurrent Chapter Requirements:",
            prompt
        ]
        return "\n".join(context_parts)

    def generate_chapter(self, chapter_number: int, prompt: str) -> None:
        """Generate a single chapter with completion verification, incorporating new agents in the flow - WITH STATUS UPDATES"""
        logger.info(f"Generating Chapter {chapter_number}")
        logger.debug(f"Chapter prompt: {prompt[:200]}...")

        try:
            groupchat = self.initiate_group_chat()
            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config=self.agent_config
            )

            context = self._prepare_chapter_context(chapter_number, prompt)
            chapter_prompt = f"""
            IMPORTANT: This is Chapter {chapter_number}. Focus ONLY on this chapter. Do not proceed to the next chapter until explicitly instructed.
            IMPORTANT: Wait for confirmation after each agent's step before proceeding to the next.

            Current Task: Generate Chapter {chapter_number} content only, following a detailed, step-by-step process.

            Chapter Outline:
            Title: {self.outline[chapter_number - 1]['title']}

            Chapter Requirements:
            {prompt}

            Previous Context for Reference:
            {context}

            Follow this strict sequence for generating Chapter {chapter_number}:

            1. Memory Keeper: Review previous chapters and current outline. Provide a MEMORY UPDATE summarizing relevant context for this chapter. (Tag: MEMORY UPDATE)
            2. Story Planner: Based on the chapter outline and overall story arc, provide a detailed PLAN for this chapter, focusing on plot progression and pacing. (Tag: PLAN)
            3. Setting Builder: Detail the SETTING for this chapter, ensuring it is vivid and consistent with the world-building. (Tag: SETTING)
            4. Character Agent: Outline specific CHARACTER developments and actions for key characters within this chapter, maintaining character arcs. (Tag: CHARACTER)
            5. Plot Agent: Refine the CHAPTER PLOT and pacing for this chapter based on the outline and overall story arc, focusing on key events and engagement. (Tag: PLOT)
            6. Writer: Based on ALL preceding plans and outlines, write a complete SCENE DRAFT for Chapter {chapter_number}. Ensure it meets the minimum word count and incorporates all elements. (Tag: SCENE DRAFT)
            7. Editor: Review the SCENE DRAFT for quality, consistency, outline alignment, and length. Provide FEEDBACK and suggest revisions, or approve if satisfactory. (Tag: FEEDBACK)
            8. Writer Final: Revise the scene based on editor feedback to create the SCENE FINAL for Chapter {chapter_number}. (Tag: SCENE FINAL)
            9. User Proxy: CONFIRMATION: Verify chapter completion, quality, and length. Proceed to the next chapter only upon explicit confirmation of successful finalization of Chapter {chapter_number}. (Tag: CONFIRMATION)

            Wait for each step to be confirmed before proceeding to the next agent. Ensure each agent completes their tagged output before moving forward."""

            print(f"\nGenerating Chapter {chapter_number}: {self.outline[chapter_number - 1]['title']}")  # Status update - Chapter start

            print(f"  1. Memory Keeper: Preparing context...")  # Status update - Memory Keeper start
            logger.info(f"Chapter prompt: {chapter_prompt}")  # Log the full prompt
            self.agents["user_proxy"].initiate_chat(
                manager,
                message=chapter_prompt,
                silent=True  # Silence default autogen output to avoid duplicate prints
            )
            print(f"  1. Memory Keeper: Context provided.")  # Status update - Memory Keeper end

            # Log all messages after initiate_chat
            logger.info(f"All messages in groupchat: {groupchat.messages}")

            if not self._verify_chapter_complete(groupchat.messages):
                logger.debug(f"Chapter {chapter_number} verification failed")
                raise ValueError(f"Chapter {chapter_number} generation incomplete")

            print(f"  2. Story Planner: Chapter plan...")  # Status update - Story Planner start (if included)
            # No specific agent call here as it's part of the group chat flow

            print(f"  3. Setting Builder: Defining settings...")  # Status update - Setting Builder start (if included)
            # No specific agent call here as it's part of the group chat flow

            print(f"  4. Character Agent: Character development...")  # Status update - Character Agent start (if included)
            # No specific agent call here as it's part of the group chat flow

            print(f"  5. Plot Agent: Refining plot...")  # Status update - Plot Agent start (if included)
            # No specific agent call here as it's part of the group chat flow

            print(f"  6. Writer: Writing scene draft...")  # Status update - Writer start
            # No specific agent call here as it's part of the group chat flow

            print(f"  7. Editor: Reviewing draft...")  # Status update - Editor start
            # No specific agent call here as it's part of the group chat flow

            print(f"  8. Writer Final: Revision and finalization...")  # Status update - Writer Final start
            # No specific agent call here as it's part of the group chat flow

            print(f"  9. User Proxy: Final confirmation...")  # Status update - User Proxy start
            # No specific agent call here as it's part of the group chat flow

            self._process_chapter_results(chapter_number, groupchat.messages)

            # Log extracted content before saving
            final_content = self._extract_final_scene(groupchat.messages)
            logger.info(f"Extracted content for chapter {chapter_number}: {final_content[:500]}...")

            chapter_file = os.path.join(self.output_dir, f"chapter_{chapter_number:02d}.txt")
            if not os.path.exists(chapter_file):
                logger.debug(f"Chapter file missing: {chapter_file}")
                raise FileNotFoundError(f"Chapter {chapter_number} file not created")

            completion_msg = f"Chapter {chapter_number} is complete. Proceed with next chapter."
            self.agents["user_proxy"].send(completion_msg, manager, silent=True)  # Silence proxy send message

            print(f"Chapter {chapter_number}: {self.outline[chapter_number - 1]['title']} - GENERATION COMPLETE")  # Status update - Chapter complete

        except Exception as e:
            logger.error(f"Error in chapter {chapter_number}: {str(e)}")
            logger.exception("Full stack trace:")
            logger.debug(f"Chapter {chapter_number} error context: {prompt[:200]}...")
            self._handle_chapter_generation_failure(chapter_number, prompt)

    def _extract_final_scene(self, messages: List[Dict]) -> Optional[str]:
        """Extract chapter content with improved content detection"""
        for msg in reversed(messages):
            content = msg.get("content", "")
            sender = self._get_sender(msg)

            if sender == "writer_final" and "SCENE FINAL:" in content:
                scene_text = content.split("SCENE FINAL:")[1].strip()
                if scene_text:
                    scene_lines = []
                    for line in scene_text.split('\n'):
                        if not any(marker in line.upper() for marker in [
                            "KEY EVENTS:", "CHARACTER DEVELOPMENTS:",
                            "SETTING:", "TONE:", "PLAN:", "OUTLINE:",
                            "MEMORY UPDATE:", "FEEDBACK:"
                        ]):
                            scene_lines.append(line)
                    return '\n'.join(scene_lines)

        for msg in reversed(messages):
            content = msg.get("content", "")
            sender = self._get_sender(msg)

            if sender == "writer" and "SCENE FINAL:" in content:
                scene_text = content.split("SCENE FINAL:")[1].strip()
                if scene_text:
                    scene_lines = []
                    for line in scene_text.split('\n'):
                        if not any(marker in line.upper() for marker in [
                            "KEY EVENTS:", "CHARACTER DEVELOPMENTS:",
                            "SETTING:", "TONE:", "PLAN:", "OUTLINE:",
                            "MEMORY UPDATE:", "FEEDBACK:"
                        ]):
                            scene_lines.append(line)
                    return '\n'.join(scene_lines)

        return None

    def _handle_chapter_generation_failure(self, chapter_number: int, prompt: str) -> None:
        """Handle failed chapter generation with simplified retry"""
        logger.warning(f"Attempting simplified retry for Chapter {chapter_number}")

        try:
            retry_groupchat = autogen.GroupChat(
                agents=[
                    self.agents["user_proxy"],
                    self.agents["story_planner"],
                    self.agents["writer"]
                ],
                messages=[],
                max_round=3
            )

            manager = autogen.GroupChatManager(
                groupchat=retry_groupchat,
                llm_config=self.agent_config
            )

            # Exclude ollama_base_url from retry config to avoid TypeError - Hypothesis 1 Fix
            retry_llm_config = {k: v for k, v in self.agent_config.items() if k != 'ollama_base_url'}

            retry_prompt = f"""Emergency chapter generation for Chapter {chapter_number}.

{prompt}

Retry LLM Config (no ollama_base_url):
{retry_llm_config}

Please generate this chapter in two steps:
1. Story Planner: Create a basic outline (tag: PLAN)
2. Writer: Write the complete chapter (tag: SCENE FINAL)

Keep it simple and direct."""

            logger.debug(f"Retry Prompt for Chapter {chapter_number}: {retry_prompt}") # ADDED: Log retry_prompt
            logger.debug(f"Retry LLM Config for Chapter {chapter_number}: {retry_llm_config}") # ADDED: Log retry_llm_config

            self.agents["user_proxy"].initiate_chat(
                manager,
                llm_config=retry_llm_config, # Use modified config WITHOUT ollama_base_url - Hypothesis 1 Fix
                message=retry_prompt
            )

            self._process_chapter_results(chapter_number, retry_groupchat.messages)

        except Exception as e:
            logger.error(f"Error in retry attempt for Chapter {chapter_number}: {str(e)}")
            logger.error("Unable to generate chapter content after retry")
            raise

    def _process_chapter_results(self, chapter_number: int, messages: List[Dict]) -> None:
        """Process and save chapter results, updating memory - now also extracts character/world updates"""
        try:
            memory_updates = []
            world_updates = []  # Capture world updates
            character_updates = []  # Capture character updates

            for msg in reversed(messages):
                sender = self._get_sender(msg)
                content = msg.get("content", "")

                if sender == "memory_keeper":
                    if "MEMORY UPDATE:" in content:
                        update_start = content.find("MEMORY UPDATE:") + 14
                        memory_updates.append(content[update_start:].strip())
                    if "WORLD:" in content:  # Extract world updates
                        world_update_start = content.find("WORLD:") + 6
                        world_updates.append(content[world_update_start:].strip())
                    if "CHARACTER:" in content:  # Extract character updates
                        character_update_start = content.find("CHARACTER:") + 10
                        character_updates.append(content[character_update_start:].strip())
                    if memory_updates and world_updates and character_updates:  # Get only the latest updates
                        break

            if memory_updates:
                self.chapters_memory.append(memory_updates[0])
            else:
                chapter_content = self._extract_final_scene(messages)
                if chapter_content:
                    basic_summary = f"Chapter {chapter_number} Summary: {chapter_content[:200]}..."
                    self.chapters_memory.append(basic_summary)

            # Process world updates
            if world_updates:
                for update_text in world_updates:
                    # Simple parsing - needs to be robust for real use
                    world_name_match = re.search(r"WORLD:\s*([\w\s]+):", update_text)  # Example: WORLD: Location Name: Description
                    desc_match = re.search(r"Description:\s*(.+)", update_text, re.DOTALL)
                    if world_name_match and desc_match:
                        world_name = world_name_match.group(1).strip()
                        description = desc_match.group(1).strip()
                        self.agents["setting_builder"].update_world_element(world_name, description)  # Use setting_builder to update
                        logger.info(f"Updated world element '{world_name}': {description[:50]}...")

            # Process character updates
            if character_updates:
                for update_text in character_updates:
                    char_name_match = re.search(r"CHARACTER:\s*([\w\s]+):", update_text)  # Example: CHARACTER: Character Name: Development
                    dev_match = re.search(r"Development:\s*(.+)", update_text, re.DOTALL)
                    if char_name_match and dev_match:
                        char_name = char_name_match.group(1).strip()
                        development = dev_match.group(1).strip()
                        self.agents["character_agent"].update_character_development(char_name, development)  # Use character_agent to update
                        logger.info(f"Updated character '{char_name}' development: {development[:50]}...")

            self._save_chapter(chapter_number, messages)

        except Exception as e:
            logger.error(f"Error processing chapter results: {str(e)}")
            raise

    def _save_chapter(self, chapter_number: int, messages: List[Dict]) -> None:
        """Save the final chapter content to a file"""
        logger.info(f"Saving Chapter {chapter_number}")
        try:
            final_content = None
            for msg in reversed(messages):
                content = msg.get("content", "")
                sender = self._get_sender(msg)

                if sender == "writer_final" and "SCENE FINAL:" in content:
                    final_content = content.split("SCENE FINAL:")[1].strip()
                    break

            if not final_content:
                for msg in reversed(messages):
                    content = msg.get("content", "")
                    sender = self._get_sender(msg)

                    if sender == "writer" and "SCENE FINAL:" in content:
                        final_content = content.split("SCENE FINAL:")[1].strip()
                        break

            if not final_content:
                raise ValueError(f"No final content found for Chapter {chapter_number}")

            final_content = self._clean_chapter_content(final_content)

            content_sections = final_content.split('---')
            final_content = '\n\n'.join([
                section.strip() for section in content_sections
                if not any(marker in section.upper() for marker in [
                    "MEMORY UPDATE:", "FEEDBACK:", "PLAN:", "OUTLINE:", "SETTING:", "CHARACTER:", "PLOT:"  # Added new tags to remove
                ])
            ]).strip()

            content_lines = []
            for line in final_content.split('\n'):
                if not line.strip().startswith((
                    "KEY EVENTS:", "CHARACTER DEVELOPMENTS:",
                    "SETTING:", "TONE:", "THE CHAPTER",
                    "CONTINUES TO", "EXPLORES", "CONCLUDES WITH"
                )):
                    content_lines.append(line)

            final_content = '\n'.join(content_lines).strip()

            if len(final_content.split()) < 100:
                raise ValueError("Chapter content too short after cleaning")

            filename = os.path.join(self.output_dir, f"chapter_{chapter_number:02d}.txt")

            if os.path.exists(filename):
                backup_filename = f"{filename}.backup"
                import shutil
                shutil.copy2(filename, backup_filename)

            with open(filename, "w", encoding='utf-8') as f:
                f.write(f"Chapter {chapter_number}\n\n{final_content}")

            with open(filename, "r", encoding='utf-8') as f:
                saved_content = f.read()
                if len(saved_content.strip()) == 0:
                    raise IOError(f"File {filename} is empty")

            logger.info(f"Saved chapter to: {filename}")

        except Exception as e:
            logger.error(f"Error saving chapter: {str(e)}")
            raise

    def generate_book(self, outline: List[Dict]) -> None:
        """Generate the book with strict chapter sequencing and verification"""
        logger.info("Starting book generation")
        logger.info(f"Total chapters: {len(outline)}")

        sorted_outline = sorted(outline, key=lambda x: x["chapter_number"])
        self._generate_table_of_contents()

        for chapter in sorted_outline:
            chapter_number = chapter["chapter_number"]

            if chapter_number > 1:
                prev_file = os.path.join(self.output_dir, f"chapter_{chapter_number-1:02d}.txt")
                if not os.path.exists(prev_file):
                    logger.error(f"Previous chapter {chapter_number-1} not found. Stopping.")
                    break

                with open(prev_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not self._verify_chapter_content([{"content": content}], chapter_number-1): # Pass content as list of dict
                        logger.error(f"Previous chapter {chapter_number-1} content invalid. Stopping.")
                        break

            logger.info(f"Starting Chapter {chapter_number}")
            self.generate_chapter(chapter_number, chapter["prompt"])

            chapter_file = os.path.join(self.output_dir, f"chapter_{chapter_number:02d}.txt")
            if not os.path.exists(chapter_file):
                logger.error(f"Failed to generate chapter {chapter_number}")
                break

            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not self._verify_chapter_content([{"content": content}], chapter_number): # Pass content as list of dict
                    logger.error(f"Chapter {chapter_number} content invalid")
                    break

            logger.info(f"Chapter {chapter_number} complete")
            time.sleep(5)

    def _verify_chapter_content(self, messages: List[Dict], chapter_number: int) -> bool:
        """Verify chapter content is valid"""
        if not messages:
            logger.debug(f"Chapter {chapter_number}: No messages found.")
            return False

        content = messages[-1].get("content", "") if messages else ""
        if not content:
            logger.debug(f"Chapter {chapter_number} content is empty")
            return False

        if f"Chapter {chapter_number}" not in content:
            logger.debug(f"Chapter {chapter_number} header missing")
            return False

        lines = content.split('\n')
        content_lines = [line for line in lines if line.strip() and 'MEMORY UPDATE:' not in line]

        valid = len(content_lines) >= 3
        logger.debug(f"Chapter {chapter_number} content validation: {valid}")
        return valid