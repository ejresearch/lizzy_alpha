# 📚 Available Story Templates & Outlines

## 🎉 **What You Now Have Access To**

Thanks to the legacy import, you now have **proven, tested story structures** with complete templates and rich examples!

---

## 📖 **Template 1: Classic 27-Scene Romantic Comedy**

**Source**: Elle & EsteandTheo projects  
**Structure**: 3 acts with precise beat structure  
**Best for**: Traditional romantic comedies, two-person love stories  

### **Full Beat Sheet Available:**
- **Act I** (8 scenes): Setup → Meet Cute → Connection
- **Act II** (10 scenes): Collaboration → Romance → Conflict
- **Act III** (9 scenes): Resolution → Grand Gesture → Happy Ending

### **Complete Example** (EsteandTheo):
```
Scene 1: Opening Image - Coastal town, Este (writer) + Theodore (photographer)
Scene 2: Meet Cute - Coffee spill on vintage camera
Scene 12: Past Comes Back - Ex returns, threatens new relationship
Scene 23: Grand Gesture - Public apology at festival ceremony
Scene 27: Final Image - Walking hand-in-hand on boardwalk
```

**Characters Available**: 6 fully developed with romantic challenges, traits, flaws

---

## 🎬 **Template 2: Extended 34-Scene Ensemble Drama**

**Source**: TNK_A4 project  
**Structure**: 5 acts with love triangle complexity  
**Best for**: Multi-character stories, complex relationship dynamics  

### **Structure Highlights:**
- **Wedding setting** for natural character introductions
- **Love triangle dynamics** (Emily, Patrick, Archie)
- **Extended development** for deeper character exploration
- **Multiple relationship threads** woven together

### **Example Opening** (TNK_A4):
```
Scene 1: Wedding rehearsal dinner - Emily coordinates, meets Patrick
Scene 5: Wedding reception - Archie appears, creates tension
Scene 9: Post-wedding reality check - Friends analyze the situation
```

**Characters Available**: 7 developed characters with detailed romantic challenges

---

## 🎭 **Template 3: Alternative Structures** 

Based on additional imported data and brainstorming history:

### **Variation A: Fast-Paced Rom-Com** (24 scenes)
- Condensed 3-act structure
- Quick pacing for modern audiences
- Focus on witty dialogue and chemistry

### **Variation B: Friends-to-Lovers** (30 scenes)
- Extended friendship development
- Slower romantic progression
- Emphasis on emotional foundation

---

## 📊 **How to Use These Templates**

### **1. Start with a Template**
```bash
python3 start.py          # Create new project
python3 intake.py         # Select outline template
```

### **2. Customize the Structure**
- **Keep core beats** (Meet Cute, Midpoint, Grand Gesture)
- **Adjust scene count** for your story needs
- **Modify specific elements** for your genre/setting

### **3. AI-Enhanced Development**
```bash
python3 brainstorm.py     # Get scene-specific ideas
python3 write.py          # Generate draft content
```

The AI knows these structures and will generate content that fits the beats!

---

## 🎯 **Beat Definitions & Examples**

### **Essential Romantic Comedy Beats:**

| Beat | Purpose | Example (EsteandTheo) |
|------|---------|----------------------|
| **Opening Image** | Establish world/characters | Este with rejection letters, Theodore with camera |
| **Meet Cute** | Memorable first encounter | Coffee spill accident in café |
| **Inciting Incident** | Event that forces them together | Community center committee assignment |
| **Midpoint** | Peak romantic tension | Almost kiss interrupted |
| **All Is Lost** | Relationship seems impossible | Major misunderstanding erupts |
| **Grand Gesture** | Public declaration of love | Theodore recreates coffee spill at festival |
| **Final Image** | Show transformed relationship | Hand-in-hand on boardwalk |

### **Character Arc Elements:**

| Element | Purpose | Example |
|---------|---------|---------|
| **Romantic Challenge** | Core relationship obstacle | "Struggles to open up due to past heartbreak" |
| **Lovable Trait** | What makes them appealing | "Witty, kind, and relentlessly optimistic" |
| **Comedic Flaw** | Source of humor | "Clumsiness leads to hilarious mishaps" |

---

## 🚀 **Quick Start Templates**

### **Template A: Classic Meet Cute**
1. Opening Image - Show protagonists in separate worlds
2. Meet Cute - Accidental encounter with spark
3. Early Banter - Witty exchange reveals chemistry
4. Their Real Lives - Show individual challenges
5. Forced Together - External event requires collaboration
... (continue with 27-scene structure)

### **Template B: Workplace Romance**  
1. Opening Image - Show work environment
2. New Colleague - Professional introduction
3. Professional Tension - Conflicting work styles
4. After-Hours Connection - Personal side revealed
5. Project Partnership - Must work closely together
... (adapt remaining beats)

### **Template C: Second Chance Romance**
1. Opening Image - Show current separate lives  
2. Unexpected Return - Ex comes back to town
3. Awkward Reunion - Past tension surfaces
4. Changed People - Show how they've grown
5. Old Spark - Chemistry still there despite history
... (continue with modified beats)

---

## 💾 **Accessing Template Data**

All templates are stored in your imported projects:

```bash
# View complete 27-scene structure
sqlite3 projects/EsteandTheo/EsteandTheo.sqlite "SELECT act, scene, scene_title, beat FROM story_outline ORDER BY act, scene;"

# View rich character examples  
sqlite3 projects/EsteandTheo/EsteandTheo.sqlite "SELECT name, romantic_challenge, lovable_trait, comedic_flaw FROM characters;"

# View 34-scene extended structure
sqlite3 projects/TNK_A4/TNK_A4.sqlite "SELECT act, scene, key_events FROM story_outline ORDER BY act, scene;"
```

---

## 🎨 **AI Integration Notes**

The lizzy_alpha AI system understands these templates because:

1. **Database Schema** includes beat/structure fields
2. **Brainstorming Module** references scene purposes  
3. **Writing Module** uses character traits and story beats
4. **Knowledge Buckets** contain examples of these structures

When you ask for scene ideas, the AI will automatically:
- **Reference the beat** (Setup, Midpoint, etc.)
- **Use character traits** (romantic challenges, flaws)
- **Follow genre conventions** from knowledge buckets
- **Maintain story consistency** across your outline

---

**🎉 You now have professional-grade story templates with working examples, rich character development, and AI integration ready to use!**