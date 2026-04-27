import base64
import os
import json
from openai import OpenAI
from tqdm import tqdm
import time
import argparse

def get_path_from_image_name(name: str):
    path = "../data/mini_original_images/"
    path += f"{name}.png"
    if os.path.exists(path):
        print(f"image '{name}' exists")
        return path
    else:
        print(f"image '{name}' not exist")
        return "not_exist"
    


def get_image_encode(image_name: str):
    print("image_name",image_name)
    image_path = get_path_from_image_name(image_name)
    if image_path!="not_exist":
        print(image_path)
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    else:
        return "not_exist"

def is_valid_json(text):
    """
    Determine whether a string can be parsed to legitimate JSON.
    """
    try:
        json.loads(text)  # try parse
        return True
    except json.JSONDecodeError:
        return False

def response_correct(text):
    """
    See if the response is fine
    """
    try:
        result=text.choices[0].message.content
        return True
    except Exception as e:
        return False



client = OpenAI(
    base_url="replace_with_your_base_url",
    api_key="replace_with_your_key",
    timeout=120
)

def create_completion(model: str,toevaluate_model, path_toevaluate, savefile_path: str):
    # try:
    with open(path_toevaluate, 'r', encoding='utf-8') as file:
        data = json.load(file)
    index=0 #problem count
    imgproblem_list=[]
    jsonproblem_list=[]
    responseproblem_list=[]
    TruePos_list=[]
    with tqdm(total=len(data), desc="Progress of topic processing") as pbar:
        for key in data:
            Step_by_step_evaluation=data[key]["o4-mini_evaluate"]["Step_by_step_evaluation"]
            #Only evaluate questions that are wrong in the process
            if Step_by_step_evaluation!="null" and Step_by_step_evaluation!=[] and 0 in Step_by_step_evaluation:
                
                problem_text= data[key]["problem_text"]
                problem_text= "题目：\n"+problem_text
                type=data[key]["type"]
                choices=data[key]["choices"]
                if choices!=[]:
                    problem_text += "？下列哪个选项是正确的？"
                    problem_text += "\n".join(choices)
                number_answer=data[key]["number_answer"]
                reference_solution= data[key]["solution"]
                reference_solution= "\n参考求解过程：\n"+reference_solution
                    
                student_answer=str(data[key][f"{toevaluate_model}_answer"])
                student_answer="\n学生解答：\n"+student_answer
                image_path=data[key]["original_image_name"]
                Step_by_step_evaluation=data[key]["o4-mini_evaluate"]["Step_by_step_evaluation"]
                Error_location="\n每一步正确性为:"+f"{Step_by_step_evaluation}"
                if type=="Calculation":      
                    with open(prompt_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        problem_text =problem_text+"正确的数值答案为："+number_answer
                else:
                    with open(prompt_path, 'r', encoding='utf-8') as file:
                        text = file.read()   
                
                text = text+problem_text+reference_solution+student_answer+Error_location+"/n下面请分析错误步骤的错误原因和错误类型："  #组成了完整prompt
                print(text)
                image_info = get_image_encode(image_path)#such as input 1_1
                if image_info=="not_exist":
                    imgproblem_list.append(key)
                    continue
                max_attempts=3
                for attempt in range(max_attempts):
                    try:
                        print(f"trying{attempt}")
                        response = client.chat.completions.create(
                            model=model,
                            max_tokens=8192,
                            temperature= 0.1,
                            messages= [{
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/png;base64,{image_info}"},
                                    },
                                    {"type": "text", "text": text},
                                ],
                            }],
                        )
                        if response.choices[0].message.content!="":
                            break
                        if response.choices[0].message.content==""and attempt < max_attempts - 1:
                            print("empty",response.choices[0].message.content)
                            continue
                    except Exception as e:
                        print("str(e)",str(e))
                        response=f"{str(e)}"
                        if attempt < max_attempts - 1:
                            time.sleep(1)
                            continue
                        
                print("response",response)
                if response_correct(response):
                    result=response.choices[0].message.content
                    print("result",result)
                    #formatted for JSON format
                    cleaned_text = result.replace("\n", "")  # DELETE \n
                    cleaned_text = cleaned_text.replace("\\", "")  # DELETE \
                    cleaned_text = cleaned_text.replace("```", "")  # DELETE `
                    cleaned_text = cleaned_text.replace("json", "")  # DELETE json
                    cleaned_text = cleaned_text.replace("> Reasoned for a couple of seconds", "")  # DELETE thinking
                    if '{'in text:
                        first_brace_index = cleaned_text.find('{')
                        cleaned_text= cleaned_text[first_brace_index:]
                    
                    if(is_valid_json(cleaned_text)):
                        result_json = json.loads(cleaned_text)
                        data[key][f"error_analyze"] = result_json
                    else:
                        data[key][f"error_analyze"] = cleaned_text
                        jsonproblem_list.append(key)
                    with open(savefile_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    index +=1
                    print(f"{index} question has been processed")
                    pbar.update(1)  
                else:
                    result=response
                    data[key][f"error_analyze"] = f"response_error with {result}"
                    with open(savefile_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    responseproblem_list.append(key)
                    index +=1
                    print(f"{index} Processing failed")
                    pbar.update(1)  
            else:
                #Error-free processes do not require error analysis
                data[key][f"error_analyze"] = f"There is no need for error type analysis"
                with open(savefile_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                TruePos_list.append(key) #Records keys that do not require error analysis
                index +=1
                print(f"Skip the {index} question")
                pbar.update(1)  
                                   


    print("imgproblem_list",imgproblem_list)
    print("jsonproblem_list",jsonproblem_list)
    print("responseproblem_list",responseproblem_list)
    

def parse_arguments():
    parser = argparse.ArgumentParser(description='Error analysis for different LMMs\' solution.')
    parser.add_argument('--evaluator', type=str, default="o4-mini", help='The model to evaluate others')
    parser.add_argument('--model_name', type=str, required=True, help='The model to be evaluated')
    parser.add_argument('--input_json', type=str, required=True, help='Directory containing the solution JSON files.')
    parser.add_argument('--output_json', type=str, required=True, help='Directory containing the result JSON files.')
    return parser.parse_args()

# Main entry point 
if __name__ == "__main__":
    
    prompt_path = 'prompts/analyze_error.txt'
    args = parse_arguments()
    tasks = create_completion(args.evaluator,args.model_name,args.input_json,args.output_json)
