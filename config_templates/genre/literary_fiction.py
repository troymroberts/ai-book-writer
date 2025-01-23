"""
Literary Fiction Configuration Template
Focused on character-driven narratives with deep themes and psychological complexity.
"""

# Character Elements
CHARACTER_DEPTH = 0.9                # Base complexity of character development
CHARACTER_PERSONALITY_DEPTH = 0.9    # Psychological and emotional layers
CHARACTER_VOICE_CONSISTENCY = 0.9    # Distinct speech patterns and internal monologue
CHARACTER_RELATIONSHIP_DEPTH = 0.9   # Complexity of interpersonal dynamics
CHARACTER_ARC_TYPE = "complex"       # Options: "complex", "gradual", "subtle", "transformative"
CHARACTER_BACKSTORY_DEPTH = 0.8      # Integration of past experiences
CHARACTER_MOTIVATION_COMPLEXITY = 0.9 # Layered character motivations
CHARACTER_PSYCHOLOGY = 0.9           # Depth of psychological exploration
EMOTIONAL_RESONANCE = 0.9           # Emotional impact of character experiences
INTERNAL_CONFLICT_DEPTH = 0.9       # Complexity of internal struggles

# Narrative Structure
MULTI_THREADED_PLOTTING = True      # Multiple interweaving plot lines
PLOT_COMPLEXITY = 0.8               # Intricacy of plot elements
FORESHADOWING_FREQUENCY = 0.8       # Integration of future story elements
THEME_REINFORCEMENT = 0.9           # Consistency of thematic elements
SUBPLOT_DENSITY = 0.7               # Quantity and complexity of subplots
PLOT_RESOLUTION_STYLE = "nuanced"   # Options: "nuanced", "open_ended", "circular", "ambiguous"
NARRATIVE_LAYERING = 0.9            # Multiple levels of meaning
STRUCTURAL_INNOVATION = 0.8         # Experimental narrative structures
TIME_TREATMENT = "nonlinear"        # Options: "nonlinear", "fragmented", "circular", "layered"
PERSPECTIVE_SHIFTS = 0.7            # Frequency of viewpoint changes

# Scene Construction
SCENE_PACING_VARIETY = 0.8          # Mix of contemplative and dynamic scenes
SENSORY_DETAIL_DEPTH = 0.9          # Richness of sensory descriptions
TENSION_CURVE_CONTROL = 0.7         # Management of scene-level tension
DIALOGUE_AUTHENTICITY = 0.9         # Naturalistic dialogue style
SETTING_INTEGRATION = 0.8           # Setting as character/theme reflection
SCENE_TRANSITIONS = "fluid"         # Options: "fluid", "abrupt", "thematic", "associative"
ATMOSPHERIC_DENSITY = 0.9           # Richness of mood and atmosphere
SYMBOLISM_IN_SETTING = 0.9         # Use of setting for symbolic meaning
TEMPORAL_FLOW = "variable"         # Options: "variable", "compressed", "expanded"
DETAIL_SELECTION = "significant"    # Options: "significant", "atmospheric", "psychological"

# Style Elements
NARRATIVE_STYLE = "third_person_limited" # Narrative perspective
PROSE_COMPLEXITY = 0.8              # Sophistication of language
SYMBOLISM_DENSITY = 0.9             # Frequency of symbolic elements
METAPHOR_FREQUENCY = 0.8            # Use of metaphorical language
SUBTEXT_DEPTH = 0.9                 # Layers of unstated meaning
LANGUAGE_INNOVATION = 0.7           # Experimental language use
SENTENCE_VARIETY = 0.9              # Mix of sentence structures
RHYTHM_CONTROL = 0.8                # Prose rhythm management
DICTION_SOPHISTICATION = 0.9        # Vocabulary and word choice
STYLISTIC_CONSISTENCY = 0.9         # Maintenance of style

# Thematic Elements
THEME_COMPLEXITY = 0.9              # Depth of thematic exploration
MORAL_AMBIGUITY = 0.9              # Complexity of moral questions
PHILOSOPHICAL_DEPTH = 0.8           # Integration of philosophical ideas
SOCIAL_COMMENTARY_LEVEL = 0.7       # Degree of social observation
PSYCHOLOGICAL_EXPLORATION = 0.9      # Depth of psychological themes
CULTURAL_RESONANCE = 0.8            # Connection to broader human experience
INTELLECTUAL_ENGAGEMENT = 0.9       # Complexity of ideas explored
METAPHYSICAL_CONTENT = 0.7          # Exploration of existential questions
SYMBOLIC_RESONANCE = 0.9            # Depth of symbolic meaning
THEMATIC_LAYERING = 0.9             # Multiple interacting themes
THEME_FOCUS = "isolation"          # Suggested themes: "isolation", "redemption", "identity", "loss", "connection" # Setting a specific thematic focus for generation

# Literary Techniques
STREAM_OF_CONSCIOUSNESS = 0.7       # Use of stream-of-consciousness
UNRELIABLE_NARRATION = 0.6          # Degree of narrator unreliability
METAFICTIONAL_ELEMENTS = 0.5        # Self-referential elements
INTERTEXTUALITY = 0.6               # References to other texts
EXPERIMENTAL_TECHNIQUES = 0.6        # Use of innovative literary devices

# Advanced Writing Features
MOTIF_DEVELOPMENT = 0.8             # Recurring symbolic elements
IMAGERY_PATTERNS = 0.9              # Consistent image systems
PSYCHOLOGICAL_ACUITY = 0.9          # Insight into human nature
EMOTIONAL_MODULATION = 0.8          # Control of emotional resonance
NARRATIVE_DISTANCE = "variable"      # Options: "variable", "close", "distant", "oscillating"

# Pacing - Granular Chapter Pacing Control
PACING_SPEED_CHAPTER_START = 0.3     # Slower pace at chapter beginnings for setup
PACING_SPEED_CHAPTER_MID = 0.6       # Moderate pace in chapter middle for development
PACING_SPEED_CHAPTER_END = 0.5       # Slightly slower pace at chapter ends for reflection

# Human Characteristics Settings - Keep these at 1.0 for Literary Fiction to maximize nuance
SHOW_DONT_TELL = 1.0
SUBTEXT_NUANCE = 1.0
PERSONAL_OPINIONS = 1.0
COLLOQUIAL_EXPRESSIONS = 1.0
LOGICAL_LEAPS = 1.0
SUBJECTIVE_EXPRESSIONS = 1.0
RHETORICAL_TECHNIQUES = 1.0
PERSONAL_EXPERIENCES = 1.0
CHARACTER_DEVELOPMENT = 1.0
NATURAL_FLOW = 1.0

####################################################################################################
# Example Prompts - How to use these settings effectively in chapter outlines
####################################################################################################

# Example Chapter Outline using Literary Fiction Template Settings:

# Chapter 1: The Weight of Silence (Example for slow start, high character/emotional depth)
# --------------------------------------------------
# [Using high CHARACTER_DEPTH, EMOTIONAL_DEPTH, PACING_SPEED_CHAPTER_START]
# Focus: Introduce the protagonist, ELARA, in a moment of quiet solitude that reveals her internal state of isolation (THEME_FOCUS = "isolation").
# Key Events:
# - Elara sits alone in her sparsely furnished apartment, overlooking the rainy cityscape. Describe her sensory experience - the chill, the muted sounds of the city, the taste of stale coffee. (SENSORY_DETAIL_DEPTH high)
# - Flashback (brief, fragmented - TIME_TREATMENT = "nonlinear") to a recent, failed attempt at connection - a strained phone call with her mother. (CHARACTER_BACKSTORY_DEPTH, CHARACTER_RELATIONSHIP_DEPTH)
# - Elara notices a small, antique music box on her shelf, a relic from her grandmother. It triggers a deeper, more melancholic reflection on her family history and recurring patterns of loneliness. (SYMBOLISM_IN_SETTING, THEME_COMPLEXITY)
# Character Developments:
# - Establish Elara's profound sense of isolation and emotional distance from others. Show her internal monologue - introspective, articulate, but tinged with resignation. (CHARACTER_VOICE_CONSISTENCY, INTERNAL_CONFLICT_DEPTH)
# - Hint at a past trauma or series of disappointments that have led to her current state, without explicit exposition. (SUBTEXT_DEPTH)
# Setting:
# - Elara's apartment - cold, minimalist, reflecting her emotional interior. Emphasize the grayness of the urban landscape outside, mirroring her mood. (ATMOSPHERIC_DENSITY, SETTING_INTEGRATION)
# Tone:
# - Melancholy, introspective, quiet, heavy with unspoken emotion. (EMOTIONAL_RESONANCE)
# - Use a NARRATIVE_DISTANCE = "close" to keep focus tightly on Elara's internal experience.


# Chapter 2: Echoes in the Gallery (Example for building tension, introducing subplot)
# --------------------------------------------------
# [Using moderate PACING_SPEED_CHAPTER_MID, TENSION_CURVE_CONTROL, SUBPLOT_DENSITY]
# Focus: Elara's routine at the art gallery is disrupted by a subtle, unsettling encounter, hinting at a shift in her isolated world.
# Key Events:
# - Describe Elara's daily routine at the gallery - precise, almost ritualistic, emphasizing her need for control and order in her environment. (SCENE_PACING_VARIETY - start with slower pace)
# - A new visitor, MARK, enters the gallery and shows an unusual, intense interest in a painting that resonates deeply with Elara's own feelings of isolation. (PLOT_COMPLEXITY - introduce new character, potential subplot)
# - Dialogue between Elara and Mark - initially formal, but with subtle undertones of curiosity and shared understanding. Dialogue should be naturalistic but revealing of character. (DIALOGUE_AUTHENTICITY)
# - Elara observes Mark after he leaves, noticing something slightly off or unsettling about his demeanor, creating a sense of unease. (TENSION_CURVE_CONTROL - build subtle tension)
# Character Developments:
# - Elara's carefully constructed emotional barriers are slightly breached by her interaction with Mark. Show subtle shifts in her internal monologue - a flicker of curiosity, a hint of vulnerability beneath her detached exterior. (CHARACTER_PSYCHOLOGY, EMOTIONAL_MODULATION)
# - Introduce Mark as an enigmatic figure who may become significant to Elara's arc, but keep his motivations and intentions ambiguous. (CHARACTER_MOTIVATION_COMPLEXITY)
# Setting:
# - The art gallery - initially presented as a sterile, controlled space, but subtly infused with a sense of unease and mystery as Mark enters. (ATMOSPHERIC_DENSITY - shift in atmosphere)
# - Focus on visual details within the gallery - specific paintings, shadows, lighting - that reflect the emerging tension and thematic focus. (SENSORY_DETAIL_DEPTH, SYMBOLISM_IN_SETTING)
# Tone:
# - Start with a tone of quiet routine, gradually shifting to subtle unease and intrigue. (SCENE_PACING_VARIETY, TONE - shifting tone)
# - Maintain NARRATIVE_DISTANCE = "close" to Elara, but allow glimpses of Mark from her perspective to build mystery.