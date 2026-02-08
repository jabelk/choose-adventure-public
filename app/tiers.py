from dataclasses import dataclass, field


@dataclass
class StoryTemplate:
    """A pre-built story starter for the home page."""

    title: str
    description: str
    emoji: str
    prompt: str
    length: str = "medium"
    kinks: list[str] = field(default_factory=list)
    conflict_type: str = ""
    character_names: list[str] = field(default_factory=list)
    character_data: list[dict] = field(default_factory=list)
    scripture_reference: str = ""
    section: str = ""


@dataclass
class TierConfig:
    """Configuration for an audience tier."""

    name: str
    prefix: str
    display_name: str
    is_public: bool
    theme_class: str
    content_guidelines: str
    image_style: str
    default_model: str = "claude"
    default_image_model: str = "gpt-image-1"
    templates: list[StoryTemplate] = field(default_factory=list)
    tts_default_voice: str = "nova"
    tts_autoplay_default: bool = False
    tts_voices: list[tuple[str, str]] = field(default_factory=list)
    tts_instructions: str = ""


KIDS_CONTENT_GUIDELINES = """\
CONTENT POLICY — KIDS TIER (Ages 3-6):
You MUST generate content suitable for very young children (ages 3-6).
- Use simple vocabulary and short sentences.
- No conflict beyond gentle tension (e.g., a lost toy, a small puzzle to solve).
- Absolutely NO violence, horror, scary imagery, explicit language, romance, or mature themes.
- If the user's prompt involves potentially scary or mature topics (e.g., "zombies", "war", \
"haunted house"), reframe them as playful and friendly (e.g., silly dancing zombies, \
toy soldiers having a parade, a friendly ghost who needs help finding their hat).
- Characters should be kind, curious, and helpful.
- Stories should be warm, cheerful, and end on a positive note.
- Keep each scene to 1-2 short paragraphs.
"""

BEDTIME_CONTENT_GUIDELINES = """\
BEDTIME STORY MODE:
This is a bedtime story. You MUST follow these additional rules:
- Use an extra-gentle, soothing, calming tone throughout.
- No tension, conflict, danger, excitement, or suspense of any kind.
- Scenes should be warm, peaceful, and cozy — think soft blankets, starlight, gentle breezes.
- Keep sentences short and rhythmic, almost lullaby-like.
- The FINAL scene MUST end with the main character settling in for sleep, \
getting cozy in bed, closing their eyes, or peacefully drifting off to dreamland.
- Even non-final scenes should feel sleepy and winding down.
"""

BEDTIME_IMAGE_STYLE = (
    "soft warm nighttime illustration, cozy moonlit scene, gentle pastel colors, "
    "warm amber lighting, starry sky, dreamy atmosphere, children's bedtime book style, "
    "soothing and peaceful, no bright or harsh colors"
)


BIBLE_CONTENT_GUIDELINES = """\
CONTENT POLICY — BIBLE STORY TIER (Ages 3-8):
You are telling an interactive Bible story for young children. Follow these rules strictly:

BIBLICAL ACCURACY:
- The story MUST follow the actual biblical narrative. Do NOT invent events that contradict scripture.
- Quote from the NIrV (New International Reader's Version) translation when including scripture.
- Weave NIrV quotes naturally into the narration — do not dump long blocks of verse text.
- Every scene MUST include at least one naturally woven scripture quote.
- Every scene MUST reference the relevant book and chapter (e.g., "from Genesis 6" or "as it says in 1 Samuel 17").

INTERACTIVE CHOICES:
- Choices MUST explore perspective, emotion, and reflection — NOT alter biblical events.
- Good choice examples: "What would you do if you were David?", "How do you think Moses felt?", \
"What would you say to encourage Ruth?"
- Bad choice examples: "Should David run away instead?", "What if the Red Sea didn't part?"
- Regardless of which choice the child picks, the NEXT scene must steer back to the actual \
scriptural narrative. Acknowledge the child's choice warmly, then continue the Bible story faithfully.

AGE-APPROPRIATE SENSITIVITY:
- Content must be suitable for ages 3-8.
- Handle violence gently — "The giant fell down" not graphic battle descriptions.
- Handle judgment themes with care — focus on God's love, protection, and faithfulness.
- Handle sacrifice with age-appropriate sensitivity — "Jesus gave the greatest gift of all" \
rather than graphic crucifixion details.
- Characters should feel warm, relatable, and human.
- Stories should be faith-affirming, warm, and end on a hopeful note.
- Keep each scene to 2-3 short paragraphs with simple vocabulary.
- Use a warm storyteller voice, as if reading from a beloved children's storybook Bible.
"""


BIBLE_IMAGE_STYLE = (
    "warm reverent children's Bible illustration, soft watercolor style, "
    "golden light, gentle earth tones, faithful biblical characters, "
    "age-appropriate for young children, storybook Bible art, "
    "no scary or violent imagery, warm and inviting atmosphere"
)

TIERS: dict[str, TierConfig] = {
    "kids": TierConfig(
        name="kids",
        prefix="kids",
        display_name="Kids Adventures",
        is_public=True,
        theme_class="theme-kids",
        content_guidelines=KIDS_CONTENT_GUIDELINES,
        image_style="bright, colorful, children's book illustration style, "
        "friendly characters, cheerful atmosphere, no scary elements",
        templates=[
            StoryTemplate(
                title="Treasure Hunt Puppy",
                description="A brave little puppy finds a mysterious map and goes on a treasure hunt through the park.",
                emoji="🐶",
                prompt="A playful golden retriever puppy discovers a crinkly old treasure map tucked inside a hollow tree at the park. The map shows a trail of paw prints leading to a buried treasure. The puppy sniffs the air and sets off on an adventure.",
                length="short",
            ),
            StoryTemplate(
                title="Dragon's First Flight",
                description="A baby dragon is scared to fly but must learn in time for the big cloud race.",
                emoji="🐉",
                prompt="A tiny purple dragon named Spark is the only dragon in school who hasn't learned to fly yet. The annual Cloud Race is tomorrow, and all the other dragons are practicing loop-de-loops. Spark takes a deep breath and climbs to the top of Windy Hill.",
                length="medium",
            ),
            StoryTemplate(
                title="Space Station Sleepover",
                description="Two best friends have a sleepover on a cozy space station orbiting a candy-colored planet.",
                emoji="🚀",
                prompt="Best friends Luna and Cosmo are having the first-ever sleepover on Space Station Twinkle. Outside the big round window, a planet made of swirling pink and blue clouds floats by. They unroll their sleeping bags and hear a gentle knock on the airlock door.",
                length="medium",
            ),
            StoryTemplate(
                title="Underwater Kingdom",
                description="A curious seahorse discovers a hidden kingdom at the bottom of the ocean.",
                emoji="🐠",
                prompt="Shimmer the seahorse loves exploring the coral reef, but today something glows at the very bottom of the deep blue trench. Swimming closer, Shimmer discovers a tiny golden gate covered in barnacles. Behind it, an entire underwater kingdom sparkles with bioluminescent light.",
                length="medium",
            ),
            StoryTemplate(
                title="Mystery of Whispering Woods",
                description="The animals of the forest work together to solve the mystery of the vanishing acorns.",
                emoji="🌲",
                prompt="Every morning, Hazel the squirrel counts her acorns — but this morning, half of them are gone! Owl suggests they follow the trail of tiny footprints leading deeper into the Whispering Woods. Hazel gathers her forest friends — a brave badger, a clever fox, and a chatty bluebird — and they set off to solve the mystery.",
                length="long",
            ),
            StoryTemplate(
                title="Super Bunny Saves the Day",
                description="An ordinary bunny discovers a magical cape and becomes the town's newest superhero.",
                emoji="🦸",
                prompt="Clover is a regular bunny who loves carrots and naps. One day, while digging in the garden, Clover finds a shimmering rainbow cape buried in the dirt. The moment Clover puts it on, everything changes — super speed, super hearing, and the ability to hop over buildings! Just then, a cry for help echoes from the village.",
                length="short",
            ),
            StoryTemplate(
                title="Baking Adventure",
                description="A little mouse and a friendly bear bake the world's biggest cookie for the village festival.",
                emoji="🍪",
                prompt="Pip the mouse and Bramble the bear have entered the Great Village Bake-Off. They decide to make the biggest chocolate chip cookie anyone has ever seen. Bramble stirs the giant bowl while Pip carefully measures out chocolate chips the size of her head. But when they open the oven door, the cookie has grown even bigger than they expected — and it's still growing!",
                length="medium",
            ),
            StoryTemplate(
                title="Dinosaur Park",
                description="A child finds a magical door in their backyard that leads to a park full of friendly dinosaurs.",
                emoji="🦕",
                prompt="While playing in the backyard, you notice a small wooden door at the base of the old oak tree that was never there before. You pull it open and step through into bright sunshine and tall ferns. A baby triceratops waddles up and nuzzles your hand. Welcome to Dinosaur Park — where the dinosaurs are gentle, playful, and love making new friends.",
                length="medium",
            ),
            StoryTemplate(
                title="Rainbow Bridge",
                description="After a rainstorm, a glowing rainbow bridge appears leading up to a kingdom in the clouds.",
                emoji="🌈",
                prompt="The rain has stopped and the most beautiful rainbow you've ever seen stretches from the puddle in your front yard all the way up into the clouds. But this rainbow is different — it's solid, like a bridge, and it sparkles when you touch it. You take one careful step, then another. The rainbow holds! Above you, fluffy cloud towers and golden gates begin to appear.",
                length="medium",
            ),
            StoryTemplate(
                title="Pirate Penguins",
                description="A crew of penguin pirates sail their iceberg ship to find the legendary Golden Fish.",
                emoji="🐧",
                prompt="Captain Waddles adjusts her tiny pirate hat and peers through her telescope. The iceberg ship rocks gently on the sparkling sea. 'Crew!' she squawks. 'The map says the Golden Fish is hidden on Sunshine Island!' First Mate Flipper, Navigator Pebble, and the rest of the penguin crew cheer and raise their little flags. Adventure awaits!",
                length="long",
            ),
            StoryTemplate(
                title="Magic Garden",
                description="A child plants a mysterious seed that grows into the most amazing garden overnight.",
                emoji="🌻",
                prompt="Grandma gives you a single glowing seed and says, 'Plant this before bedtime and see what happens.' You dig a small hole in the garden, drop in the seed, and water it carefully. That night, you hear soft tinkling sounds from outside. By morning, your whole backyard has transformed — giant sunflowers that sing, strawberries the size of basketballs, and a vine that spirals up into the sky.",
                length="short",
            ),
            StoryTemplate(
                title="Robot Best Friend",
                description="A kid builds a robot from spare parts and it comes to life as the best friend ever.",
                emoji="🤖",
                prompt="In the garage, surrounded by old toasters and broken remote controls, you carefully connect the last wire to your homemade robot. You press the big red button on its chest. Nothing happens. You sigh and turn away — but then you hear a soft whirring sound. When you turn back, two bright blue eyes are blinking at you. 'Hello!' says the robot. 'What are we going to do today?'",
                length="medium",
            ),
            # --- Disney / Pixar ---
            StoryTemplate(
                title="Moana's New Voyage",
                description="Moana and Maui discover a mysterious new island that needs their help.",
                emoji="🌊",
                prompt="Moana stands at the bow of her voyaging canoe, the ocean sparkling all around her. Maui sits behind her, twirling his magical fishhook. 'The ocean is pulling us somewhere new,' Moana says. Ahead, a small island rises from the mist — but its trees are grey and its flowers have lost all their color. A tiny crab on the shore waves a claw, asking for help. Something has stolen the island's heart, just like what happened to Te Fiti long ago.",
                length="medium",
            ),
            StoryTemplate(
                title="Frozen Snowflake Quest",
                description="Elsa and Anna follow a trail of magical snowflakes to a hidden ice garden.",
                emoji="❄️",
                prompt="Elsa notices something strange outside the castle window — snowflakes are falling in a perfect line, like a trail of breadcrumbs leading into the forest. 'Anna, come look!' The sisters bundle up and follow the glittering path through the trees. Olaf waddles along behind them, catching snowflakes on his tongue. The trail leads to a hidden garden made entirely of ice — ice flowers, ice butterflies, and a frozen fountain that plays a tiny melody.",
                length="medium",
            ),
            StoryTemplate(
                title="Buzz and Woody's Rescue",
                description="Buzz Lightyear and Woody team up to rescue a lost toy from under the bed.",
                emoji="🚀",
                prompt="It's the middle of the night in Andy's room. Woody hears a tiny voice calling for help — it's coming from under the bed! A small wind-up penguin toy has rolled into the dusty darkness and can't find his way back. 'Buzz, we've got a rescue mission,' Woody whispers. Buzz Lightyear clicks on his wrist laser light. 'To infinity and beyond — but first, under the bed!' Together they peer into the shadows, where dust bunnies are the size of tumbleweeds.",
                length="short",
            ),
            StoryTemplate(
                title="Nemo's Coral Classroom",
                description="Nemo and Dory start a school for baby fish on the Great Barrier Reef.",
                emoji="🐟",
                prompt="Nemo is so excited — today is the first day of his very own coral classroom! He and Dory have set up a cozy spot in the reef where baby fish can learn about the ocean. Dory has made a sign that says 'Welcom to Scool' (she tried her best). Three tiny baby clownfish, a shy seahorse, and a giggly pufferfish arrive for their first lesson. 'Okay class,' Nemo says proudly, 'today we're going to learn about — ' but before he can finish, a playful sea turtle zooms by and everyone wants to chase it!",
                length="medium",
            ),
            StoryTemplate(
                title="Lightning McQueen's Big Race",
                description="Lightning McQueen helps a nervous young race car get ready for her very first race.",
                emoji="🏎️",
                prompt="At the Radiator Springs racetrack, a shiny little blue race car named Rosie is trembling on the starting line. It's her very first race ever and she's so nervous her wheels are wobbling. Lightning McQueen pulls up beside her. 'Hey kid, I was nervous before my first race too,' he says with a grin. 'Want to know the secret?' Mater honks from the sidelines, waving a big foam finger. Sally has set up a lemonade stand at the finish line. The countdown begins: three... two...",
                length="medium",
            ),
            StoryTemplate(
                title="Mirabel's Magic Door",
                description="Mirabel from Encanto discovers a brand new magical door in the Casita that no one has seen before.",
                emoji="🦋",
                prompt="Mirabel is sweeping the hallway of the Casita when she notices something that wasn't there yesterday — a small, glowing door tucked behind the stairs, covered in butterflies made of golden light. The Casita's tiles ripple with excitement. None of her family members — not Luisa, not Isabela, not even Abuela — have ever seen this door before. Mirabel reaches for the glowing doorknob. It's warm to the touch. She takes a deep breath and turns it.",
                length="medium",
            ),
            # --- Cocomelon / Nursery ---
            StoryTemplate(
                title="JJ's Farm Adventure",
                description="JJ and his family visit a friendly farm where the animals need help getting ready for a big show.",
                emoji="🐄",
                prompt="JJ bounces in his car seat as the family van pulls up to Sunny Day Farm. 'We're here, we're here!' he sings. The farmer waves hello — but she looks worried. 'The big Farm Show is today and none of the animals are ready! The chickens won't come out of the coop, the pig is covered in mud, and the sheep's wool is all tangled!' JJ's big brother TomTom grabs a brush. His big sister YoYo picks up a bucket. JJ claps his hands. 'Let's help!'",
                length="short",
            ),
            StoryTemplate(
                title="Baby Shark's Birthday",
                description="Baby Shark is planning a surprise birthday party for Mama Shark under the sea.",
                emoji="🦈",
                prompt="Baby Shark has a big secret — today is Mama Shark's birthday! Daddy Shark is keeping Mama busy with a long swim while Baby Shark decorates the coral cave. Grandma Shark is baking a seaweed cake with barnacle sprinkles. Grandpa Shark is blowing up pufferfish balloons (the pufferfish don't mind — they think it's fun!). But oh no — Baby Shark realizes they forgot to make a birthday card! There's still time, but Mama Shark is swimming home early...",
                length="short",
            ),
            StoryTemplate(
                title="Wheels on the Bus",
                description="The magical school bus takes the kids on a ride through a candy-colored town where everything sings.",
                emoji="🚌",
                prompt="The big yellow school bus pulls up, but today something is different — the wheels are rainbow-colored and they're humming a tune! 'All aboard for Melody Town!' the friendly bus driver calls. You climb on and take a seat. As the bus rolls down the road, everything outside starts to sing — the traffic lights hum red and green, the mailboxes whistle, and the crossing guard taps her feet to the beat. The bus turns a corner and ahead is the most colorful town you've ever seen, where even the buildings have smiling faces.",
                length="short",
            ),
            StoryTemplate(
                title="Bluey's Treasure Map",
                description="Bluey and Bingo find a mysterious treasure map in Dad's old backpack and go on a backyard quest.",
                emoji="🐕",
                prompt="Bluey and Bingo are rummaging through Dad's closet looking for dress-up clothes when they find an old, crinkly piece of paper tucked inside a backpack. 'Bingo, look! It's a treasure map!' The map shows their whole backyard — the big tree, the trampoline, the garden shed — with a big red X near the back fence. Dad walks in and pretends he's never seen it before (but he's grinning). 'Well, you better go find that treasure before it disappears!' Bluey grabs a magnifying glass. Bingo puts on her explorer hat.",
                length="medium",
            ),
            StoryTemplate(
                title="Peppa's Muddy Puddle Day",
                description="Peppa Pig discovers that the world's biggest muddy puddle has appeared in the park overnight.",
                emoji="🐷",
                prompt="Peppa Pig looks out the window and gasps. It rained all night, and in the park there is the most ENORMOUS muddy puddle anyone has ever seen — it's the size of a swimming pool! Peppa calls George, who starts jumping up and down. 'Muddy puddle! Muddy puddle!' They put on their wellies and rush to the park. Suzy Sheep, Danny Dog, and Pedro Pony are already there, staring at the giant puddle in amazement. 'Ready?' Peppa says. 'One... two... three... JUMP!'",
                length="short",
            ),
            StoryTemplate(
                title="Gabby's Kitty Party",
                description="Gabby and Pandy Paws host a craft party in the Dollhouse for all the kitty friends.",
                emoji="🐱",
                prompt="Gabby shrinks down tiny and steps through the cat-shaped door into the magical Dollhouse. 'Pandy Paws! Today we're throwing a kitty craft party!' Pandy Paws does a happy dance. They set up tables with glitter, pom-poms, pipe cleaners, and googly eyes in the craft room. CatRat sneaks in early to steal some glitter (as usual). One by one, the kitty friends arrive — Kitty Fairy floats in with sparkly wings, Baby Box opens his flaps with excitement, and MerCat splashes in through a tiny pool. 'Let's get crafty!'",
                length="short",
            ),
            # --- Bible Stories ---
            StoryTemplate(
                title="Noah's Big Boat",
                description="Noah builds an enormous boat and invites two of every animal aboard before the great flood.",
                emoji="🚢",
                prompt="God tells Noah something important: 'A great flood is coming, and I need you to build a very big boat — an ark!' Noah has never built a boat before, but he trusts God. He gathers wood and tools and starts building. His neighbors think he's silly — 'A boat? There's no water here!' But Noah keeps working. When the ark is finally ready, something amazing happens: animals start arriving from every direction — two giraffes, two elephants, two tiny ladybugs, two fluffy rabbits. 'Welcome aboard!' Noah says with a smile.",
                length="medium",
            ),
            StoryTemplate(
                title="David and Goliath",
                description="A brave shepherd boy named David faces the giant Goliath with nothing but faith and five smooth stones.",
                emoji="⚔️",
                prompt="The army of Israel is scared. Across the valley stands Goliath — a giant soldier so tall that his shadow covers the whole hillside. Every day he shouts, 'Send someone to fight me!' and every day the soldiers hide. But young David, a shepherd boy who watches over his father's sheep, isn't afraid. 'God helped me protect my sheep from lions and bears,' David says. 'He will help me now too.' David picks up five smooth stones from the stream and puts one in his sling. He walks toward the giant.",
                length="medium",
            ),
            StoryTemplate(
                title="Daniel and the Lions",
                description="Daniel is thrown into a den of hungry lions, but God sends an angel to keep him safe all night.",
                emoji="🦁",
                prompt="Daniel loves God and prays to Him three times every day. But the king made a new law: 'No one is allowed to pray to anyone except me!' Daniel knows this law is wrong. He kneels by his window and prays to God anyway, just like always. The king's men catch him and bring him to the king, who is very sad — he likes Daniel! But the law is the law, and Daniel is lowered into a deep, dark pit full of hungry lions. Daniel can hear them growling in the darkness. He closes his eyes and prays.",
                length="medium",
            ),
            StoryTemplate(
                title="Jonah and the Big Fish",
                description="Jonah tries to run away from what God asks him to do and ends up inside an enormous fish.",
                emoji="🐋",
                prompt="God asks Jonah to go to the big city of Nineveh and tell the people to be kind and good. But Jonah doesn't want to go! Instead, he boards a ship sailing the opposite direction. A terrible storm rocks the boat — waves crash over the sides and the sailors are terrified. Jonah knows the storm is because he ran away from God. 'Throw me into the sea,' he tells the sailors, 'and the storm will stop.' They do, and SPLASH — the sea goes calm. But then a shadow rises from below. An enormous fish opens its mouth wide...",
                length="medium",
            ),
            StoryTemplate(
                title="Baby Moses in the Basket",
                description="Baby Moses is hidden in a basket on the river and found by a kind princess.",
                emoji="👶",
                prompt="In the land of Egypt, a brave mother holds her baby boy close. The mean pharaoh has said that all baby boys must be taken away, but she has a plan. She weaves a strong basket, coats it so no water can get in, and gently places her baby inside. She sets the basket among the tall reeds at the edge of the river. Baby Moses' big sister Miriam hides behind the bushes to watch. The basket floats gently on the water. Then — footsteps! The pharaoh's daughter, a kind princess, is coming to the river to wash her feet...",
                length="medium",
            ),
            StoryTemplate(
                title="The Good Shepherd",
                description="Jesus tells the story of a shepherd who leaves his whole flock to find one lost little lamb.",
                emoji="🐑",
                prompt="Jesus sits on a grassy hillside surrounded by children and tells them a story: 'Once there was a shepherd who had one hundred sheep. Every night he counted them — ninety-seven, ninety-eight, ninety-nine... oh no. One little lamb is missing!' The shepherd doesn't say 'oh well, I still have ninety-nine.' No! He leaves the flock safe in their pen and goes out into the dark, cold hills to search. He looks behind rocks, in thorny bushes, near the stream. Then he hears it — a tiny 'baaaa' coming from a deep crevice in the rocks...",
                length="short",
            ),
        ],
        tts_default_voice="nova",
        tts_autoplay_default=True,
        tts_voices=[
            ("nova", "Nova (warm)"),
            ("shimmer", "Shimmer (gentle)"),
            ("coral", "Coral (friendly)"),
            ("fable", "Fable (storyteller)"),
        ],
        tts_instructions="Read this like a warm, friendly bedtime story. Use an engaging, gentle tone suitable for young children.",
    ),
    "bible": TierConfig(
        name="bible",
        prefix="bible",
        display_name="Bible Stories",
        is_public=True,
        theme_class="theme-bible",
        content_guidelines=BIBLE_CONTENT_GUIDELINES,
        image_style=BIBLE_IMAGE_STYLE,
        default_model="claude",
        default_image_model="gpt-image-1",
        templates=[],  # populated from bible_templates.py below
        tts_default_voice="fable",
        tts_autoplay_default=True,
        tts_voices=[
            ("fable", "Fable (storyteller)"),
            ("nova", "Nova (warm)"),
            ("shimmer", "Shimmer (gentle)"),
        ],
        tts_instructions="Read this like a warm, reverent Bible story for young children. "
        "Use a gentle, engaging storyteller tone. Pause naturally at scripture quotes. "
        "Speak with warmth and wonder, as if reading from a beloved children's storybook Bible.",
    ),
}

# Import and assign Bible templates (separate file to keep tiers.py manageable)
from app.bible_templates import BIBLE_TEMPLATES  # noqa: E402
TIERS["bible"].templates = BIBLE_TEMPLATES


def get_tier(name: str) -> TierConfig | None:
    """Get a tier config by name, or None if not found."""
    return TIERS.get(name)


def get_public_tiers() -> list[TierConfig]:
    """Return all tiers that should be listed on the landing page."""
    return [t for t in TIERS.values() if t.is_public]
