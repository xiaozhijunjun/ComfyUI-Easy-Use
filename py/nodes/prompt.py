import os
import json
import folder_paths
from urllib.request import urlopen
from ..libs.log import log_node_info
from ..libs.wildcards import get_wildcard_list, process
from ..libs.utils import AlwaysEqualProxy
from ..config import RESOURCES_DIR, FOOOCUS_STYLES_DIR, MAX_SEED_NUM, PROMPT_TEMPLATE
from .. import easyCache

# 正面提示词
class positivePrompt:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "positive": ("STRING", {"default": "", "multiline": True, "placeholder": "Positive"}),}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("positive",)
    FUNCTION = "main"

    CATEGORY = "EasyUse/Prompt"

    @staticmethod
    def main(positive):
        return positive,

# 通配符提示词
class wildcardsPrompt:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        wildcard_list = get_wildcard_list()
        return {"required": {
            "text": ("STRING", {"default": "", "multiline": True, "dynamicPrompts": False, "placeholder": "(Support Lora Block Weight and wildcard)"}),
            "Select to add LoRA": (["Select the LoRA to add to the text"] + folder_paths.get_filename_list("loras"),),
            "Select to add Wildcard": (["Select the Wildcard to add to the text"] + wildcard_list,),
            "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED_NUM}),
            "multiline_mode": ("BOOLEAN", {"default": False}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "populated_text")
    OUTPUT_IS_LIST = (True, True)
    FUNCTION = "main"

    CATEGORY = "EasyUse/Prompt"

    def translate(self, text):
        return text

    def main(self, *args, **kwargs):
        prompt = kwargs["prompt"] if "prompt" in kwargs else None
        seed = kwargs["seed"]

        # Clean loaded_objects
        if prompt:
            easyCache.update_loaded_objects(prompt)

        text = kwargs['text']
        if "multiline_mode" in kwargs and kwargs["multiline_mode"]:
            populated_text = []
            _text = []
            text = text.split("\n")
            for t in text:
                t = self.translate(t)
                _text.append(t)
                populated_text.append(process(t, seed))
            text = _text
        else:
            text = self.translate(text)
            populated_text = [process(text, seed)]
            text = [text]
        return {"ui": {"value": [seed]}, "result": (text, populated_text)}

# 负面提示词
class negativePrompt:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "negative": ("STRING", {"default": "", "multiline": True, "placeholder": "Negative"}),}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("negative",)
    FUNCTION = "main"

    CATEGORY = "EasyUse/Prompt"

    @staticmethod
    def main(negative):
        return negative,

# 风格提示词选择器
class stylesPromptSelector:

    @classmethod
    def INPUT_TYPES(s):
        styles = ["fooocus_styles"]
        styles_dir = FOOOCUS_STYLES_DIR
        for file_name in os.listdir(styles_dir):
            file = os.path.join(styles_dir, file_name)
            if os.path.isfile(file) and file_name.endswith(".json"):
                styles.append(file_name.split(".")[0])
        return {
            "required": {
               "styles": (styles, {"default": "fooocus_styles"}),
            },
            "optional": {
                "positive": ("STRING", {"forceInput": True}),
                "negative": ("STRING", {"forceInput": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("positive", "negative",)

    CATEGORY = 'EasyUse/Prompt'
    FUNCTION = 'run'

    def run(self, styles, positive='', negative='', prompt=None, extra_pnginfo=None, my_unique_id=None):
        values = []
        all_styles = {}
        positive_prompt, negative_prompt = '', negative
        if styles == "fooocus_styles":
            file = os.path.join(RESOURCES_DIR,  styles + '.json')
        else:
            file = os.path.join(FOOOCUS_STYLES_DIR, styles + '.json')
        f = open(file, 'r', encoding='utf-8')
        data = json.load(f)
        f.close()
        for d in data:
            all_styles[d['name']] = d
        if my_unique_id in prompt:
            if prompt[my_unique_id]["inputs"]['select_styles']:
                values = prompt[my_unique_id]["inputs"]['select_styles'].split(',')

        has_prompt = False
        if len(values) == 0:
            return (positive, negative)

        for index, val in enumerate(values):
            if 'prompt' in all_styles[val]:
                if "{prompt}" in all_styles[val]['prompt'] and has_prompt == False:
                    positive_prompt = all_styles[val]['prompt'].replace('{prompt}', positive)
                    has_prompt = True
                else:
                    positive_prompt += ', ' + all_styles[val]['prompt'].replace(', {prompt}', '').replace('{prompt}', '')
            if 'negative_prompt' in all_styles[val]:
                negative_prompt += ', ' + all_styles[val]['negative_prompt'] if negative_prompt else all_styles[val]['negative_prompt']

        if has_prompt == False and positive:
            positive_prompt = positive + ', '

        return (positive_prompt, negative_prompt)

#prompt
class prompt:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"default": "", "multiline": True, "placeholder": "Prompt"}),
            "prefix": (["Select the prefix add to the text"] + PROMPT_TEMPLATE["prefix"], {"default": "Select the prefix add to the text"}),
            "subject": (["👤Select the subject add to the text"] + PROMPT_TEMPLATE["subject"], {"default": "👤Select the subject add to the text"}),
            "action": (["🎬Select the action add to the text"] + PROMPT_TEMPLATE["action"], {"default": "🎬Select the action add to the text"}),
            "clothes": (["👚Select the clothes add to the text"] + PROMPT_TEMPLATE["clothes"], {"default": "👚Select the clothes add to the text"}),
            "environment": (["☀️Select the illumination environment add to the text"] + PROMPT_TEMPLATE["environment"], {"default": "☀️Select the illumination environment add to the text"}),
            "background": (["🎞️Select the background add to the text"] + PROMPT_TEMPLATE["background"], {"default": "🎞️Select the background add to the text"}),
            "nsfw": (["🔞Select the nsfw add to the text"] + PROMPT_TEMPLATE["nsfw"], {"default": "🔞️Select the nsfw add to the text"}),
        },"hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID"},}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "doit"

    CATEGORY = "EasyUse/Prompt"

    def doit(self, *args, **kwargs):
        text = kwargs['text']
        return (text,)

#promptList
class promptList:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt_1": ("STRING", {"multiline": True, "default": ""}),
            "prompt_2": ("STRING", {"multiline": True, "default": ""}),
            "prompt_3": ("STRING", {"multiline": True, "default": ""}),
            "prompt_4": ("STRING", {"multiline": True, "default": ""}),
            "prompt_5": ("STRING", {"multiline": True, "default": ""}),
        },
            "optional": {
                "optional_prompt_list": ("LIST",)
            }
        }

    RETURN_TYPES = ("LIST", "STRING")
    RETURN_NAMES = ("prompt_list", "prompt_strings")
    OUTPUT_IS_LIST = (False, True)
    FUNCTION = "run"
    CATEGORY = "EasyUse/Prompt"

    def run(self, **kwargs):
        prompts = []

        if "optional_prompt_list" in kwargs:
            for l in kwargs["optional_prompt_list"]:
                prompts.append(l)

        # Iterate over the received inputs in sorted order.
        for k in sorted(kwargs.keys()):
            v = kwargs[k]

            # Only process string input ports.
            if isinstance(v, str) and v != '':
                prompts.append(v)

        return (prompts, prompts)

#promptLine
class promptLine:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "prompt": ("STRING", {"multiline": True, "default": "text"}),
                    "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                     "max_rows": ("INT", {"default": 1000, "min": 1, "max": 9999}),
                    },
            "hidden":{
                "workflow_prompt": "PROMPT", "my_unique_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING", AlwaysEqualProxy('*'))
    RETURN_NAMES = ("STRING", "COMBO")
    OUTPUT_IS_LIST = (True, True)
    FUNCTION = "generate_strings"
    CATEGORY = "EasyUse/Prompt"

    def generate_strings(self, prompt, start_index, max_rows, workflow_prompt=None, my_unique_id=None):
        lines = prompt.split('\n')
        # lines = [zh_to_en([v])[0] if has_chinese(v) else v for v in lines if v]

        start_index = max(0, min(start_index, len(lines) - 1))

        end_index = min(start_index + max_rows, len(lines))

        rows = lines[start_index:end_index]

        return (rows, rows)

class promptConcat:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
        },
            "optional": {
                "prompt1": ("STRING", {"multiline": False, "default": "", "forceInput": True}),
                "prompt2": ("STRING", {"multiline": False, "default": "", "forceInput": True}),
                "separator": ("STRING", {"multiline": False, "default": ""}),
            },
        }
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("prompt", )
    FUNCTION = "concat_text"
    CATEGORY = "EasyUse/Prompt"

    def concat_text(self, prompt1="", prompt2="", separator=""):

        return (prompt1 + separator + prompt2,)

class promptReplace:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                "find1": ("STRING", {"multiline": False, "default": ""}),
                "replace1": ("STRING", {"multiline": False, "default": ""}),
                "find2": ("STRING", {"multiline": False, "default": ""}),
                "replace2": ("STRING", {"multiline": False, "default": ""}),
                "find3": ("STRING", {"multiline": False, "default": ""}),
                "replace3": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "replace_text"
    CATEGORY = "EasyUse/Prompt"

    def replace_text(self, prompt, find1="", replace1="", find2="", replace2="", find3="", replace3=""):

        prompt = prompt.replace(find1, replace1)
        prompt = prompt.replace(find2, replace2)
        prompt = prompt.replace(find3, replace3)

        return (prompt,)


# 肖像大师
# Created by AI Wiz Art (Stefano Flore)
# Version: 2.2
# https://stefanoflore.it
# https://ai-wiz.art
class portraitMaster:

    @classmethod
    def INPUT_TYPES(s):
        max_float_value = 1.95
        prompt_path = os.path.join(RESOURCES_DIR, 'portrait_prompt.json')
        if not os.path.exists(prompt_path):
            response = urlopen('https://raw.githubusercontent.com/yolain/ComfyUI-Easy-Use/main/resources/portrait_prompt.json')
            temp_prompt = json.loads(response.read())
            prompt_serialized = json.dumps(temp_prompt, indent=4)
            with open(prompt_path, "w") as f:
                f.write(prompt_serialized)
            del response, temp_prompt
        # Load local
        with open(prompt_path, 'r') as f:
            list = json.load(f)
        keys = [
            ['shot', 'COMBO', {"key": "shot_list"}], ['shot_weight', 'FLOAT'],
            ['gender', 'COMBO', {"default": "Woman", "key": "gender_list"}], ['age', 'INT', {"default": 30, "min": 18, "max": 90, "step": 1, "display": "slider"}],
            ['nationality_1', 'COMBO', {"default": "Chinese", "key": "nationality_list"}], ['nationality_2', 'COMBO', {"key": "nationality_list"}], ['nationality_mix', 'FLOAT'],
            ['body_type', 'COMBO', {"key": "body_type_list"}], ['body_type_weight', 'FLOAT'], ['model_pose', 'COMBO', {"key": "model_pose_list"}], ['eyes_color', 'COMBO', {"key": "eyes_color_list"}],
            ['facial_expression', 'COMBO', {"key": "face_expression_list"}], ['facial_expression_weight', 'FLOAT'], ['face_shape', 'COMBO', {"key": "face_shape_list"}], ['face_shape_weight', 'FLOAT'], ['facial_asymmetry', 'FLOAT'],
            ['hair_style', 'COMBO', {"key": "hair_style_list"}], ['hair_color', 'COMBO', {"key": "hair_color_list"}], ['disheveled', 'FLOAT'], ['beard', 'COMBO', {"key": "beard_list"}],
            ['skin_details', 'FLOAT'], ['skin_pores', 'FLOAT'], ['dimples', 'FLOAT'], ['freckles', 'FLOAT'],
            ['moles', 'FLOAT'], ['skin_imperfections', 'FLOAT'], ['skin_acne', 'FLOAT'], ['tanned_skin', 'FLOAT'],
            ['eyes_details', 'FLOAT'], ['iris_details', 'FLOAT'], ['circular_iris', 'FLOAT'], ['circular_pupil', 'FLOAT'],
            ['light_type', 'COMBO', {"key": "light_type_list"}], ['light_direction', 'COMBO', {"key": "light_direction_list"}], ['light_weight', 'FLOAT']
        ]
        widgets = {}
        for i, obj in enumerate(keys):
            if obj[1] == 'COMBO':
                key = obj[2]['key'] if obj[2] and 'key' in obj[2] else obj[0]
                _list = list[key].copy()
                _list.insert(0, '-')
                widgets[obj[0]] = (_list, {**obj[2]})
            elif obj[1] == 'FLOAT':
                widgets[obj[0]] = ("FLOAT", {"default": 0, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider",})
            elif obj[1] == 'INT':
                widgets[obj[0]] = (obj[1], obj[2])
        del list
        return {
            "required": {
                **widgets,
                "photorealism_improvement": (["enable", "disable"],),
                "prompt_start": ("STRING", {"multiline": True, "default": "raw photo, (realistic:1.5)"}),
                "prompt_additional": ("STRING", {"multiline": True, "default": ""}),
                "prompt_end": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("positive", "negative",)

    FUNCTION = "pm"

    CATEGORY = "EasyUse/Prompt"

    def pm(self, shot="-", shot_weight=1, gender="-", body_type="-", body_type_weight=0, eyes_color="-",
           facial_expression="-", facial_expression_weight=0, face_shape="-", face_shape_weight=0,
           nationality_1="-", nationality_2="-", nationality_mix=0.5, age=30, hair_style="-", hair_color="-",
           disheveled=0, dimples=0, freckles=0, skin_pores=0, skin_details=0, moles=0, skin_imperfections=0,
           wrinkles=0, tanned_skin=0, eyes_details=1, iris_details=1, circular_iris=1, circular_pupil=1,
           facial_asymmetry=0, prompt_additional="", prompt_start="", prompt_end="", light_type="-",
           light_direction="-", light_weight=0, negative_prompt="", photorealism_improvement="disable", beard="-",
           model_pose="-", skin_acne=0):

        prompt = []

        if gender == "-":
            gender = ""
        else:
            if age <= 25 and gender == 'Woman':
                gender = 'girl'
            if age <= 25 and gender == 'Man':
                gender = 'boy'
            gender = " " + gender + " "

        if nationality_1 != '-' and nationality_2 != '-':
            nationality = f"[{nationality_1}:{nationality_2}:{round(nationality_mix, 2)}]"
        elif nationality_1 != '-':
            nationality = nationality_1 + " "
        elif nationality_2 != '-':
            nationality = nationality_2 + " "
        else:
            nationality = ""

        if prompt_start != "":
            prompt.append(f"{prompt_start}")

        if shot != "-" and shot_weight > 0:
            prompt.append(f"({shot}:{round(shot_weight, 2)})")

        prompt.append(f"({nationality}{gender}{round(age)}-years-old:1.5)")

        if body_type != "-" and body_type_weight > 0:
            prompt.append(f"({body_type}, {body_type} body:{round(body_type_weight, 2)})")

        if model_pose != "-":
            prompt.append(f"({model_pose}:1.5)")

        if eyes_color != "-":
            prompt.append(f"({eyes_color} eyes:1.25)")

        if facial_expression != "-" and facial_expression_weight > 0:
            prompt.append(
                f"({facial_expression}, {facial_expression} expression:{round(facial_expression_weight, 2)})")

        if face_shape != "-" and face_shape_weight > 0:
            prompt.append(f"({face_shape} shape face:{round(face_shape_weight, 2)})")

        if hair_style != "-":
            prompt.append(f"({hair_style} hairstyle:1.25)")

        if hair_color != "-":
            prompt.append(f"({hair_color} hair:1.25)")

        if beard != "-":
            prompt.append(f"({beard}:1.15)")

        if disheveled != "-" and disheveled > 0:
            prompt.append(f"(disheveled:{round(disheveled, 2)})")

        if prompt_additional != "":
            prompt.append(f"{prompt_additional}")

        if skin_details > 0:
            prompt.append(f"(skin details, skin texture:{round(skin_details, 2)})")

        if skin_pores > 0:
            prompt.append(f"(skin pores:{round(skin_pores, 2)})")

        if skin_imperfections > 0:
            prompt.append(f"(skin imperfections:{round(skin_imperfections, 2)})")

        if skin_acne > 0:
            prompt.append(f"(acne, skin with acne:{round(skin_acne, 2)})")

        if wrinkles > 0:
            prompt.append(f"(skin imperfections:{round(wrinkles, 2)})")

        if tanned_skin > 0:
            prompt.append(f"(tanned skin:{round(tanned_skin, 2)})")

        if dimples > 0:
            prompt.append(f"(dimples:{round(dimples, 2)})")

        if freckles > 0:
            prompt.append(f"(freckles:{round(freckles, 2)})")

        if moles > 0:
            prompt.append(f"(skin pores:{round(moles, 2)})")

        if eyes_details > 0:
            prompt.append(f"(eyes details:{round(eyes_details, 2)})")

        if iris_details > 0:
            prompt.append(f"(iris details:{round(iris_details, 2)})")

        if circular_iris > 0:
            prompt.append(f"(circular iris:{round(circular_iris, 2)})")

        if circular_pupil > 0:
            prompt.append(f"(circular pupil:{round(circular_pupil, 2)})")

        if facial_asymmetry > 0:
            prompt.append(f"(facial asymmetry, face asymmetry:{round(facial_asymmetry, 2)})")

        if light_type != '-' and light_weight > 0:
            if light_direction != '-':
                prompt.append(f"({light_type} {light_direction}:{round(light_weight, 2)})")
            else:
                prompt.append(f"({light_type}:{round(light_weight, 2)})")

        if prompt_end != "":
            prompt.append(f"{prompt_end}")

        prompt = ", ".join(prompt)
        prompt = prompt.lower()

        if photorealism_improvement == "enable":
            prompt = prompt + ", (professional photo, balanced photo, balanced exposure:1.2), (film grain:1.15)"

        if photorealism_improvement == "enable":
            negative_prompt = negative_prompt + ", (shinny skin, reflections on the skin, skin reflections:1.25)"

        log_node_info("Portrait Master as generate the prompt:", prompt)

        return (prompt, negative_prompt,)


NODE_CLASS_MAPPINGS = {
    "easy positive": positivePrompt,
    "easy negative": negativePrompt,
    "easy wildcards": wildcardsPrompt,
    "easy prompt": prompt,
    "easy promptList": promptList,
    "easy promptLine": promptLine,
    "easy promptConcat": promptConcat,
    "easy promptReplace": promptReplace,
    "easy stylesSelector": stylesPromptSelector,
    "easy portraitMaster": portraitMaster,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "easy positive": "Positive",
    "easy negative": "Negative",
    "easy wildcards": "Wildcards",
    "easy prompt": "Prompt",
    "easy promptList": "PromptList",
    "easy promptLine": "PromptLine",
    "easy promptConcat": "PromptConcat",
    "easy promptReplace": "PromptReplace",
    "easy stylesSelector": "Styles Selector",
    "easy portraitMaster": "Portrait Master",
}