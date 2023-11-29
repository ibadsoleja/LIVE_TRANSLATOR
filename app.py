import gradio as gr
import openai
import threading as th
import os



def translateoutput(text,language):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": f"You will be provided with a sentence in English, and your task is to translate it into {language}."},
    {"role": "user", "content":text}
  ]
)
    return completion.choices[0]['message']['content']
    

# Initialize a global variable to hold previous output
language_info={
    'Afrikaans': 'af',
    'English': 'en',
    'Arabic': 'ar',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Belarusian': 'be',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Chinese': 'zh',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'English': 'en',
    'Estonian': 'et',
    'Finnish': 'fi',
    'French': 'fr',
    'Galician': 'gl',
    'German': 'de',
    'Greek': 'el',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Indonesian': 'id',
    'Italian': 'it',
    'Japanese': 'ja',
    'Kannada': 'kn',
    'Kazakh': 'kk',
    'Korean': 'ko',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Macedonian': 'mk',
    'Malay': 'ms',
    'Marathi': 'mr',
    'Maori': 'mi',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Serbian': 'sr',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Spanish': 'es',
    'Swahili': 'sw',
    'Swedish': 'sv',
    'Tagalog': 'tl',
    'Tamil': 'ta',
    'Thai': 'th',
    'Turkish': 'tr',
    'Ukrainian': 'uk',
    'Urdu': 'ur',
    'Vietnamese': 'vi',
    'Welsh': 'cy',
    'Other': 'Other'
}
        
   

def translate(audio_file,lan):
    message=""

    with open(audio_file, 'rb') as f:
        result = openai.Audio.translate("whisper-1", f)
        text=result.text

        if lan=="English" or lan=="Other" or text=="":
            message=text
        else:

            text=translateoutput(text,lan)
            message=text
    th.current_thread().return_value=message

    

def transcription(audio_file,input_lang):
    global language_info

    with open(audio_file, 'rb') as f:
        if input_lang=="Other":
            result = openai.Audio.transcribe("whisper-1", f)
            th.current_thread().return_value=result.text
        else:
            result = openai.Audio.transcribe("whisper-1", f,language=language_info[input_lang])
            th.current_thread().return_value=result.text





def func(audio_file,input_lang,lan,state="",state1=""):
    
    t1 = th.Thread(target=translate, args=(audio_file,lan,))
    t2 = th.Thread(target=transcription, args=(audio_file,input_lang,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    translation_text=t1.return_value
    transcribe_text=t2.return_value
    state+=transcribe_text+" "
    state1+=translation_text+" "
    state=state.replace(".","\n")
    state1=state1.replace(".","\n")
    
    

    
    return state,state1


def gpt_api(text,language):
    if text=="":
        return ""
    if len(text)>2000:
        text=text[-2000:]
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": f"your task is to make a concise summery and useful summery from the given text in {language}."},
    {"role": "user", "content":text}
]
)
    
    message=completion.choices[0]['message']['content']
    th.current_thread().return_value=message


def make_summery(text,text1,input_lan,output_lan):
    t1=th.Thread(target=gpt_api, args=(text,input_lan,))
    t2=th.Thread(target=gpt_api, args=(text1,output_lan,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return t1.return_value,t2.return_value
  

    



def clear_output_data():


    return "","","",""


css='''#clear {background-color: ##919cbf;border-radius:5%;}
#clear:hover {background-color: #ff0000;transition: 0.5s;}
#summery {background-color: ##919cbf;border-radius:5%;}
#summery:hover {background-color:#2dcc9a ;transition: 0.5s;}
# div {background-image:url("https://images.unsplash.com/photo-1506259091721-347e791bab0f?auto=format&fit=crop&q=80&w=1470&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
# background-size: cover;
# background-position: center;
# background-repeat: no-repeat;
# background-attachment: fixed;
# color=white;!imoportant;
}
'''

with gr.Blocks(theme=gr.themes.Soft(),css=css) as app:
    
    gr.Markdown("## Bixbyte Translator ",elem_id="heading")
    gr.Markdown("### no more language barrier in meeting ",elem_classes="heading")
    
    with gr.Row():
            mic = gr.Audio(sources="microphone",streaming=True,type='filepath',label='Speak')
            
            input_lan=gr.Dropdown(choices=language_info.keys(),label="Choose Input Language please",value="English",interactive=True)
            lan=gr.Dropdown(choices=language_info.keys(),label="Choose a language for translation",value="Korean",interactive=True)
            summery=gr.Button(value="Summery",variant="secondary",size="small",elem_id="summery")
            clear_output = gr.ClearButton(value="Clear Output",variant="stop",size="small",elem_id="clear")
    with gr.Row():
        with gr.Column():
        
            text=gr.Textbox(interactive=False,label="Transcription",lines=10,max_lines=10)
            
        with gr.Column():   
            text1 = gr.Textbox(interactive=False,label="Translation",lines=10,max_lines=10,)
            st=mic.stream(func, [mic,input_lan,lan,text,text1], [text,text1],show_progress=False)
    with gr.Row():
        sumer_ts=gr.Textbox(label="Summery of Transcription",interactive=False,lines=4,max_lines=4)
        sumer_tr=gr.Textbox(label="Summery of Translation",interactive=False,lines=4,max_lines=4)
        
        # pass
        summery.click(make_summery,[text,text1,input_lan,lan],[sumer_ts,sumer_tr],cancels=[st],queue=False)
        clear_output.click(clear_output_data,[],[text,text1,sumer_tr,sumer_ts],cancels=[st],queue=False)
        # gr.update(visible=True)

app.queue()
app.launch()