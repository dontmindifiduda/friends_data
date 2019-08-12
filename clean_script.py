def clean_line(line):
    if line == '' or line == None:
        return 'delete'
    elif line[0] == '[':
        return 'scene'
    elif line[0] == '(' and line[-1] == ')': 
        return 'direction'
    elif ':' in line:
        return 'character'
    elif line == "Opening Credits":
        return 'credits'
    elif line == 'Commercial Break':
        return 'commercials'
    elif line == 'End':
        return 'end'
    else:
        return 'dialogue'

def remove_returns(line):
    if line != None:
        return line.replace('\n', '')

def read_file(file_path):
    df = pd.read_csv(file_path, header=None)
    df.columns = ['lines']
    print(file_path)
    # Get episode title
    
    title = file_path.replace('friendsscraper/spiders/ep-', '')
    
    # Get list of episode writers
#     if '&' in df[0][1].split(":")[1]:
#         writers = list(map(str.strip, df[0][1].split(":")[1].split('&')))
#     else: 
#         writers = list(df[0][1])
    
    
    print(title)
    
    # Remove rows that will not be included in analysis
    script = df[df.lines.str.contains('[', regex=False).idxmax():]
    
    script = script.applymap(remove_returns)
    script['clean_code'] = list(map(clean_line, script['lines']))
    script.set_index('clean_code', inplace=True)
    
    if 'delete' in script.index:
        script.drop('delete', axis=0, inplace=True)
    
    lines = script['lines'].values
    
    return (lines, title) #, writers)

def clean_scenes(scene):
    if scene not in [None, 'Opening Credits', 'End', 'Commercial Break']:
        return scene.replace('[Scene:', '').replace(']', '').replace(')', '').replace('\xa0', '').strip()
    else:
        return scene
    
def dir_from_scene(scene):
    if scene not in [None, 'Opening Credits', 'End', 'Commercial Break']:
        return ' '.join(scene.split(',')[1:])
    else: 
        return None

def isolate_scene(scene):
    if scene not in [None, 'Opening Credits', 'End', 'Commercial Break']:
        return scene.split(',')[0]
    else:
        return scene
    
def clean_directions(direction):
    if direction != None:
        return direction.replace('(', '').replace(')', '')
    else:
        return direction
    
def text_clean(line):
    if line != None and type(line) != list:
        return line.lower().strip().translate(str.maketrans('', '', string.punctuation))
    else: 
        return line

def process_script(lines, title): #, writers):

    dialogue = []
    character = []
    scene = []
    episode = []
    direction = []
    # written_by = []
    
    def update_lists(dia, char, scn, ep, direct): #, wrt):
        dialogue.append(dia)
        character.append(char)
        scene.append(scn)
        episode.append(ep)
        direction.append(direct)
        #written_by.append(wrt)

    current_scene = None
    current_dialogue = None
    current_character = None

    i = 0 

    while i < len(lines):
        if 'Scene:' in lines[i]:
            current_scene = lines[i]
            current_dialogue = None
            current_character = None

        elif lines[i][0] == '(' and lines[i][-1] == ')':
            current_character = None
            current_dialogue = None
            update_lists(current_dialogue, current_character, current_scene, title, lines[i])# , writers)

        elif ':' in lines[i]:
            current_character = lines[i].split(':')[0]
            current_dialogue = None
        elif (lines[i] == 'Opening Credits' or lines[i] == 'Commercial Break') or lines[i] == 'End':
            current_character = None
            current_dialogue = None  
            update_lists(current_dialogue, current_character, lines[i], title, None) #, writers)
            
        else:
            if current_dialogue == None:
                current_dialogue = lines[i]
            else:
                current_dialogue += ' ' + lines[i]

        if i + 1 < len(lines) and current_dialogue != None and (lines[i+1][0] == '[' or (lines[i][0] == '(' and lines[i+1][-1] == ')') or ':' in lines[i+1] or lines[i+1] == 'Opening Credits' or lines[i+1] == 'Commercial Break' or lines[i+1] == 'End'):
            update_lists(current_dialogue, current_character, current_scene, title, None) #, writers)


        i += 1
    
    script_df = pd.DataFrame(list(zip(episode, scene, direction, character, dialogue)), columns=['episode', 'scene', 'direction', 'characters', 'dialogue'])
    
    script_df['scene']  = list(map(clean_scenes, script_df['scene']))
    
    for i in range(len(script_df)):
        if i == 0 or script_df['scene'][i] != script_df['scene'][i-1]:
            script_df['direction'][i] = dir_from_scene(script_df['scene'][i])
            
    for i in range(len(script_df)):
        if script_df['dialogue'][i] != None and '(' in script_df['dialogue'][i]:
            script_df['direction'][i] = script_df['dialogue'][i][script_df['dialogue'][i].find("(") + 1:script_df['dialogue'][i].find(")")]
            script_df['dialogue'][i] = re.sub(r'\([^()]*\)', '', script_df['dialogue'][i])
    

        
    script_df['scene'] = list(map(isolate_scene, script_df['scene']))
    script_df['direction'] = list(map(clean_directions, script_df['direction']))
    
    return script_df.applymap(text_clean)

