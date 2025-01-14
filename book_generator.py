"""Main class for generating books using AutoGen with improved iteration control"""
import autogen
from typing import Dict, List, Optional
import os
import time
import re
import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)

class BookGenerator:
    def __init__(self, agents: Dict[str, autogen.ConversableAgent], agent_config: Dict, outline: List[Dict]):
        """Initialize with outline to maintain chapter count context"""
        self.agents = agents
        self.agent_config = agent_config
        self.output_dir = "book_output"
        self.chapters_memory = []  # Store chapter summaries
        self.max_iterations = 3  # Limit editor-writer iterations
        self.outline = outline  # Store the outline
        os.makedirs(self.output_dir, exist_ok=True)

    def _clean_chapter_content(self, content: str) -> str:
        """Clean up chapter content while preserving meaningful text"""
        # Remove chapter number references in parentheses
        content = re.sub(r'\(Chapter \d+.*?\)', '', content)
        
        # Remove markdown artifacts but preserve emphasis
        content = content.replace('**', '')
        content = content.replace('__', '')
        
        # Remove empty lines and excessive whitespace
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
        """Create a new group chat for the agents with improved speaking order"""
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
                self.agents["writer"],
                self.agents["editor"],
                writer_final
            ],
            messages=messages,
            max_round=5,
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
            'plan': False,
            'setting': False,
            'scene': False,
            'feedback': False,
            'scene_final': False,
            'confirmation': False
        }
        
        # Analyze full conversation
        for msg in messages:
            content = msg.get("content", "")
            sender = self._get_sender(msg)
            
            # Track chapter number
            if not current_chapter:
                num_match = re.search(r"Chapter (\d+):", content)
                if num_match:
                    current_chapter = int(num_match.group(1))
            
            # Track completion sequence
            if "MEMORY UPDATE:" in content: sequence_complete['memory_update'] = True
            if "PLAN:" in content: sequence_complete['plan'] = True
            if "SETTING:" in content: sequence_complete['setting'] = True
            if "SCENE:" in content: sequence_complete['scene'] = True
            if "FEEDBACK:" in content: sequence_complete['feedback'] = True
            if "SCENE FINAL:" in content and sender in ["writer_final", "writer"]:
                sequence_complete['scene_final'] = True
                has_final_content = True
            if "**Confirmation:**" in content and "successfully" in content:
                sequence_complete['confirmation'] = True

            logger.debug(f"Sequence complete: {sequence_complete}")
            logger.debug(f"Current chapter: {current_chapter}")
            logger.debug(f"Has final content: {has_final_content}")
        
        # Verify all steps completed and content exists
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
        """Generate a single chapter with completion verification"""
        logger.info(f"Generating Chapter {chapter_number}")
        logger.debug(f"Chapter prompt: {prompt[:200]}...")  # Log first 200 chars of prompt
        
        try:
            # Create group chat with reduced rounds
            groupchat = self.initiate_group_chat()
            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config=self.agent_config
            )

            # Prepare context
            context = self._prepare_chapter_context(chapter_number, prompt)
            chapter_prompt = f"""
            IMPORTANT: Wait for confirmation before proceeding.
            IMPORTANT: This is Chapter {chapter_number}. Do not proceed to next chapter until explicitly instructed.
            DO NOT END THE STORY HERE unless this is actually the final chapter ({self.outline[-1]['chapter_number']}).

            Current Task: Generate Chapter {chapter_number} content only.

            Chapter Outline:
            Title: {self.outline[chapter_number - 1]['title']}

            Chapter Requirements:
            {prompt}

            Previous Context for Reference:
            {context}

            Follow this exact sequence for Chapter {chapter_number} only:

            1. Memory Keeper: Context (MEMORY UPDATE)
            2. Writer: Draft (CHAPTER)
            3. Editor: Review (FEEDBACK)
            4. Writer Final: Revision (CHAPTER FINAL)

            Wait for each step to complete before proceeding."""

            # Start generation
            self.agents["user_proxy"].initiate_chat(
                manager,
                message=chapter_prompt
            )

            if not self._verify_chapter_complete(groupchat.messages):
                logger.debug(f"Chapter {chapter_number} verification failed")
                raise ValueError(f"Chapter {chapter_number} generation incomplete")
        
            self._process_chapter_results(chapter_number, groupchat.messages)
            chapter_file = os.path.join(self.output_dir, f"chapter_{chapter_number:02d}.txt")
            if not os.path.exists(chapter_file):
                logger.debug(f"Chapter file missing: {chapter_file}")
                raise FileNotFoundError(f"Chapter {chapter_number} file not created")
        
            completion_msg = f"Chapter {chapter_number} is complete. Proceed with next chapter."
            self.agents["user_proxy"].send(completion_msg, manager)
            
        except Exception as e:
            logger.error(f"Error in chapter {chapter_number}: {str(e)}")
            logger.debug(f"Chapter {chapter_number} error context: {prompt[:200]}...")
            self._handle_chapter_generation_failure(chapter_number, prompt)

    def _extract_final_scene(self, messages: List[Dict]) -> Optional[str]:
        """Extract chapter content with improved content detection"""
        # First try to find SCENE FINAL from writer_final
        for msg in reversed(messages):
            content = msg.get("content", "")
            sender = self._get_sender(msg)
            
            if sender == "writer_final" and "SCENE FINAL:" in content:
                scene_text = content.split("SCENE FINAL:")[1].strip()
                if scene_text:
                    # Remove any remaining planning or outline content
                    scene_lines = []
                    for line in scene_text.split('\n'):
                        if not any(marker in line.upper() for marker in [
                            "KEY EVENTS:", "CHARACTER DEVELOPMENTS:", 
                            "SETTING:", "TONE:", "PLAN:", "OUTLINE:",
                            "MEMORY UPDATE:", "FEEDBACK:"
                        ]):
                            scene_lines.append(line)
                    return '\n'.join(scene_lines)
        
        # If no SCENE FINAL from writer_final, try writer's SCENE FINAL
        for msg in reversed(messages):
            content = msg.get("content", "")
            sender = self._get_sender(msg)
            
            if sender == "writer" and "SCENE FINAL:" in content:
                scene_text = content.split("SCENE FINAL:")[1].strip()
                if scene_text:
                    # Remove any remaining planning or outline content
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
            # Create a new group chat with just essential agents
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

            retry_prompt = f"""Emergency chapter generation for Chapter {chapter_number}.
            
{prompt}

Please generate this chapter in two steps:
1. Story Planner: Create a basic outline (tag: PLAN)
2. Writer: Write the complete chapter (tag: SCENE FINAL)

Keep it simple and direct."""

            self.agents["user_proxy"].initiate_chat(
                manager,
                message=retry_prompt
            )
            
            # Save the retry results
            self._process_chapter_results(chapter_number, retry_groupchat.messages)
            
        except Exception as e:
            logger.error(f"Error in retry attempt for Chapter {chapter_number}: {str(e)}")
            logger.error("Unable to generate chapter content after retry")
            raise

    def _process_chapter_results(self, chapter_number: int, messages: List[Dict]) -> None:
        """Process and save chapter results, updating memory"""
        try:
            # Extract the Memory Keeper's final summary
            memory_updates = []
            for msg in reversed(messages):
                sender = self._get_sender(msg)
                content = msg.get("content", "")
                
                if sender == "memory_keeper" and "MEMORY UPDATE:" in content:
                    update_start = content.find("MEMORY UPDATE:") + 14
                    memory_updates.append(content[update_start:].strip())
                    break
            
            # Add to memory even if no explicit update (use basic content summary)
            if memory_updates:
                self.chapters_memory.append(memory_updates[0])
            else:
                # Create basic memory from chapter content
                chapter_content = self._extract_final_scene(messages)
                if chapter_content:
                    basic_summary = f"Chapter {chapter_number} Summary: {chapter_content[:200]}..."
                    self.chapters_memory.append(basic_summary)
            
            # Extract and save the chapter content
            self._save_chapter(chapter_number, messages)
            
        except Exception as e:
            logger.error(f"Error processing chapter results: {str(e)}")
            raise

    def _save_chapter(self, chapter_number: int, messages: List[Dict]) -> None:
        """Save the final chapter content to a file"""
        logger.info(f"Saving Chapter {chapter_number}")
        try:
            # Extract final content from messages
            final_content = None
            for msg in reversed(messages):
                content = msg.get("content", "")
                sender = self._get_sender(msg)
                
                if sender == "writer_final" and "SCENE FINAL:" in content:
                    final_content = content.split("SCENE FINAL:")[1].strip()
                    break
            
            if not final_content:
                # Try getting content from writer if writer_final didn't provide it
                for msg in reversed(messages):
                    content = msg.get("content", "")
                    sender = self._get_sender(msg)
                    
                    if sender == "writer" and "SCENE FINAL:" in content:
                        final_content = content.split("SCENE FINAL:")[1].strip()
                        break
            
            if not final_content:
                raise ValueError(f"No final content found for Chapter {chapter_number}")
            
            # Clean up the content
            final_content = self._clean_chapter_content(final_content)
            
            # Remove metadata sections but preserve content
            content_sections = final_content.split('---')
            final_content = '\n\n'.join([
                section.strip() for section in content_sections 
                if not any(marker in section.upper() for marker in [
                    "MEMORY UPDATE:", "FEEDBACK:", "PLAN:", "OUTLINE:"
                ])
            ]).strip()
            
            # Remove specific metadata lines but keep surrounding content
            content_lines = []
            for line in final_content.split('\n'):
                if not line.strip().startswith((
                    "KEY EVENTS:", "CHARACTER DEVELOPMENTS:", 
                    "SETTING:", "TONE:", "THE CHAPTER",
                    "CONTINUES TO", "EXPLORES", "CONCLUDES WITH"
                )):
                    content_lines.append(line)
            
            final_content = '\n'.join(content_lines).strip()
            
            # Ensure minimum content length
            if len(final_content.split()) < 100:  # At least 100 words
                raise ValueError("Chapter content too short after cleaning")
            
            # Save the content
            filename = os.path.join(self.output_dir, f"chapter_{chapter_number:02d}.txt")
            
            # Create backup if file exists
            if os.path.exists(filename):
                backup_filename = f"{filename}.backup"
                import shutil
                shutil.copy2(filename, backup_filename)
            
            with open(filename, "w", encoding='utf-8') as f:
                f.write(f"Chapter {chapter_number}\n\n{final_content}")
            
            # Verify file
            with open(filename, "r", encoding='utf-8') as f:
                saved_content = f.read()
                if len(saved_content.strip()) == 0:
                    raise IOError(f"File {filename} is empty")
            
            logger.info(f"Saved chapter to: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving chapter: {str(e)}")
            raise

    def generate_book(self, outline: List[Dict]) -> None:
        """Generate the book with strict chapter sequencing"""
        logger.info("Starting book generation")
        logger.info(f"Total chapters: {len(outline)}")
        
        # Sort outline by chapter number
        sorted_outline = sorted(outline, key=lambda x: x["chapter_number"])
        
        # Generate table of contents
        self._generate_table_of_contents()
        
        for chapter in sorted_outline:
            chapter_number = chapter["chapter_number"]
            
            # Verify previous chapter exists and is valid
            if chapter_number > 1:
                prev_file = os.path.join(self.output_dir, f"chapter_{chapter_number-1:02d}.txt")
                if not os.path.exists(prev_file):
                    logger.error(f"Previous chapter {chapter_number-1} not found. Stopping.")
                    break
                    
                # Verify previous chapter content
                with open(prev_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not self._verify_chapter_content(content, chapter_number-1):
                        logger.error(f"Previous chapter {chapter_number-1} content invalid. Stopping.")
                        break
            
            # Generate current chapter
            logger.info(f"Starting Chapter {chapter_number}")
            self.generate_chapter(chapter_number, chapter["prompt"])
            
            # Verify current chapter
            chapter_file = os.path.join(self.output_dir, f"chapter_{chapter_number:02d}.txt")
            if not os.path.exists(chapter_file):
                logger.error(f"Failed to generate chapter {chapter_number}")
                break
                
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if not self._verify_chapter_content(content, chapter_number):
                    logger.error(f"Chapter {chapter_number} content invalid")
                    break
                    
            logger.info(f"Chapter {chapter_number} complete")
            time.sleep(5)

    def _verify_chapter_content(self, content: str, chapter_number: int) -> bool:
        """Verify chapter content is valid"""
        if not content:
            logger.debug(f"Chapter {chapter_number} content is empty")
            return False
            
        # Check for chapter header
        if f"Chapter {chapter_number}" not in content:
            logger.debug(f"Chapter {chapter_number} header missing")
            return False
            
        # Ensure content isn't just metadata
        lines = content.split('\n')
        content_lines = [line for line in lines if line.strip() and 'MEMORY UPDATE:' not in line]
        
        valid = len(content_lines) >= 3  # At least chapter header + 2 content lines
        logger.debug(f"Chapter {chapter_number} content validation: {valid}")
        return valid
