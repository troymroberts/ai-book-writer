import autogen
from typing import Dict, List
import re
import litellm
from llm.litellm_base import LiteLLMBase 
from llm.litellm_implementations import OllamaImplementation

class OutlineGenerator:
   def __init__(self, agents: Dict[str, autogen.ConversableAgent], agent_config: Dict):
       self.agents = agents
       self.agent_config = agent_config

   def generate_outline(self, initial_prompt: str, num_chapters: int = 25) -> List[Dict]:
       """Generate a book outline based on initial prompt"""
       print("\nGenerating outline...")

       litellm_messages = [{
           "role": "user", 
           "content": f"""Create a {num_chapters}-chapter outline:

{initial_prompt}

Output format for each chapter:
Chapter N: [Title]
Title: [Same title]
Key Events:
- [Event 1]
- [Event 2]
- [Event 3]
Character Developments: [Development details]
Setting: [Setting details]
Tone: [Tone details]

End with 'END OF OUTLINE'"""
       }]

       try:
           response = litellm.completion(
               model="ollama/deepseek-r1:14b",
               messages=litellm_messages,
               base_url="http://localhost:11434"
           )
           
           outline_content = response.choices[0].message.content
           return self._process_outline_results([{"content": outline_content}], num_chapters)

       except Exception as e:
           print(f"Error generating outline: {str(e)}")
           return self._emergency_outline_processing([], num_chapters)

   def _get_sender(self, msg: Dict) -> str:
       """Helper to get sender from message regardless of format"""
       return msg.get("sender") or msg.get("name", "")

   def _extract_outline_content(self, messages: List[Dict]) -> str:
       """Extract outline content from messages with better error handling"""
       print("Searching for outline content in messages...")

       for msg in reversed(messages):
           content = msg.get("content", "")
           if "OUTLINE:" in content:
               start_idx = content.find("OUTLINE:")
               end_idx = content.find("END OF OUTLINE")

               if start_idx != -1:
                   if end_idx != -1:
                       return content[start_idx:end_idx].strip()
                   else:
                       return content[start_idx:].strip()

       for msg in reversed(messages):
           content = msg.get("content", "")
           if "Chapter 1:" in content or "**Chapter 1:**" in content:
               return content

       return ""

   def _process_outline_results(self, messages: List[Dict], num_chapters: int) -> List[Dict]:
       """Extract and process the outline with strict format requirements"""
       outline_content = self._extract_outline_content(messages)

       if not outline_content:
           print("No structured outline found, attempting emergency processing...")
           return self._emergency_outline_processing(messages, num_chapters)

       chapters = []
       chapter_sections = re.split(r'Chapter \d+:', outline_content)

       for i, section in enumerate(chapter_sections[1:], 1):
           try:
               title_match = re.search(r'\*?\*?Title:\*?\*?\s*(.+?)(?=\n|$)', section, re.IGNORECASE)
               events_match = re.search(r'\*?\*?Key Events:\*?\*?\s*(.*?)(?=\*?\*?Character Developments:|$)', section, re.DOTALL | re.IGNORECASE)
               character_match = re.search(r'\*?\*?Character Developments:\*?\*?\s*(.*?)(?=\*?\*?Setting:|$)', section, re.DOTALL | re.IGNORECASE)
               setting_match = re.search(r'\*?\*?Setting:\*?\*?\s*(.*?)(?=\*?\*?Tone:|$)', section, re.DOTALL | re.IGNORECASE)
               tone_match = re.search(r'\*?\*?Tone:\*?\*?\s*(.*?)(?=\*?\*?Chapter \d+:|$)', section, re.DOTALL | re.IGNORECASE)

               if not title_match:
                   title_match = re.search(r'\*?\*?Chapter \d+:\s*(.+?)(?=\n|$)', section)

               if not all([title_match, events_match, character_match, setting_match, tone_match]):
                   print(f"Missing required components in Chapter {i}")
                   missing = []
                   if not title_match: missing.append("Title")
                   if not events_match: missing.append("Key Events")
                   if not character_match: missing.append("Character Developments")
                   if not setting_match: missing.append("Setting")
                   if not tone_match: missing.append("Tone")
                   print(f"  Missing: {', '.join(missing)}")
                   continue

               chapter_info = {
                   "chapter_number": i,
                   "title": title_match.group(1).strip(),
                   "prompt": "\n".join([
                       f"- Key Events: {events_match.group(1).strip()}",
                       f"- Character Developments: {character_match.group(1).strip()}",
                       f"- Setting: {setting_match.group(1).strip()}",
                       f"- Tone: {tone_match.group(1).strip()}"
                   ])
               }

               events = re.findall(r'-\s*(.+?)(?=\n|$)', events_match.group(1))
               if len(events) < 3:
                   print(f"Chapter {i} has fewer than 3 events")
                   continue

               chapters.append(chapter_info)

           except Exception as e:
               print(f"Error processing Chapter {i}: {str(e)}")
               continue

       if len(chapters) < num_chapters:
           raise ValueError(f"Only processed {len(chapters)} valid chapters out of {num_chapters} required")

       return chapters

   def _verify_chapter_sequence(self, chapters: List[Dict], num_chapters: int) -> List[Dict]:
       """Verify and fix chapter numbering"""
       chapters.sort(key=lambda x: x['chapter_number'])

       for i, chapter in enumerate(chapters, 1):
           chapter['chapter_number'] = i

       while len(chapters) < num_chapters:
           next_num = len(chapters) + 1
           chapters.append({
               'chapter_number': next_num,
               'title': f'Chapter {next_num}',
               'prompt': '- Key events: [To be determined]\n- Character developments: [To be determined]\n- Setting: [To be determined]\n- Tone: [To be determined]'
           })

       chapters = chapters[:num_chapters]
       return chapters

   def _emergency_outline_processing(self, messages: List[Dict], num_chapters: int) -> List[Dict]:
       """Emergency processing when normal outline extraction fails"""
       print("Attempting emergency outline processing...")

       chapters = []
       current_chapter = None

       for msg in messages:
           content = msg.get("content", "")
           lines = content.split('\n')

           for line in lines:
               chapter_match = re.search(r'Chapter (\d+)', line)
               if chapter_match and "Key events:" in content:
                   if current_chapter:
                       chapters.append(current_chapter)

                   current_chapter = {
                       'chapter_number': int(chapter_match.group(1)),
                       'title': line.split(':')[-1].strip() if ':' in line else f"Chapter {chapter_match.group(1)}",
                       'prompt': []
                   }

               if current_chapter and line.strip().startswith('-'):
                   current_chapter['prompt'].append(line.strip())

           if current_chapter and current_chapter.get('prompt'):
               current_chapter['prompt'] = '\n'.join(current_chapter['prompt'])
               chapters.append(current_chapter)
               current_chapter = None

       if not chapters:
           print("Emergency processing failed to find any chapters")
           chapters = [
               {
                   'chapter_number': i,
                   'title': f'Chapter {i}',
                   'prompt': '- Key events: [To be determined]\n- Character developments: [To be determined]\n- Setting: [To be determined]\n- Tone: [To be determined]'
               }
               for i in range(1, num_chapters + 1)
           ]

       return self._verify_chapter_sequence(chapters, num_chapters)