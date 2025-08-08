import json
from collections import defaultdict
import numpy as np
import math

def get_weighted_score(step_eva_list):
    """
    Calculate the weighted activation process quality score of the question
    """
    n = len(step_eva_list)
    total_weighted_score = 0.0
    total_weight = 0.0
    if step_eva_list=="null":
        return 0.0  # 
    else:
        if n == 0:
            return 0.0  
        if n == 1:
            total_score= step_eva_list[0] * 1
            return total_score
        elif n > 1:    
            total_score = 0.0
            for i, value in enumerate(step_eva_list):
                # Item 0 of the list corresponds to x=1, item 1 corresponds to x=2, and so on
                x = i + 1
                # e^(-x/n)
                weight = math.exp(-x / n)
                # Cumulative weighted score
                total_weighted_score += value * weight
                # Accumulate total weight
                total_weight += weight


            if total_weight == 0:
                return 0.0  # Avoid dividing by zero
            else:
                normalized_score = total_weighted_score / total_weight
                # ***Apply the tanh activation function***
                activated_score = math.tanh(3.5 * (normalized_score - 1))+1
                return activated_score
            
def count_three_metrics(data,model):

    initmap=defaultdict(list)
    step_group_map_acc=defaultdict(list)
    step_group_map_tps=defaultdict(list)
    process_score=[]

    print("model","model")

    for key in data:
        Step_by_step_evaluation=data[key]["o4-mini_evaluate"]["Step_by_step_evaluation"]
        weighted_score=get_weighted_score(Step_by_step_evaluation)
        Final_judgment=data[key]["o4-mini_evaluate"]["Final_judgment"]
        # print("Step_by_step_evaluation",Step_by_step_evaluation)
        if Step_by_step_evaluation!="null" and Step_by_step_evaluation!=[]:
            if 0 not in Step_by_step_evaluation and Final_judgment==1:
                Truepos=1
            else:
                Truepos=0
        else:
            Truepos=0
        stepscount=data[key]["step_length"]
        process_score.append(weighted_score)
        initmap[0].append(Truepos)
        initmap[1].append(Final_judgment)
        if stepscount>=1 and stepscount<=4:
            step_group_map_acc["14"].append(Final_judgment)
            step_group_map_tps["14"].append(Truepos)
        elif stepscount>=5 and stepscount<=8:
            step_group_map_acc["58"].append(Final_judgment)
            step_group_map_tps["58"].append(Truepos)
        elif stepscount>=9 and stepscount<=12:
            step_group_map_acc["912"].append(Final_judgment)
            step_group_map_tps["912"].append(Truepos)
        elif stepscount>=13 and stepscount<=24:
            step_group_map_acc["1328"].append(Final_judgment)
            step_group_map_tps["1328"].append(Truepos)


    # print("step_group_map_acc",step_group_map_acc)
    average_acc_by_step = {}
    for step, acc_list in step_group_map_acc.items():
        if acc_list: 
            average_acc_by_step[step]=round(sum(acc_list) / len(acc_list),3)
        else:
            average_acc_by_step[step] = 0.0 
    average_tps_by_step = {}
    for step, tps_list in step_group_map_tps.items():
        if tps_list: 
            average_tps_by_step[step]=round(sum(tps_list) / len(tps_list),3)
        else:
            average_tps_by_step[step] = 0.0 

    
    average_init_pos = {}
    for metric, pos_list in initmap.items():
        if pos_list: 
            if metric==0:
                average_init_pos[0] =round(sum(pos_list) / len(pos_list),3)
            elif metric==1:
                average_init_pos[1] =round(sum(pos_list) / len(pos_list),3)
        else:
            average_init_pos[metric] = 0.0 
  
    average_process_score=round(sum(process_score)/len(process_score),3)

    # save as a dict
    all_information={}
    all_information["average_pcs"]=average_init_pos[0]
    all_information["average_acs"]=average_init_pos[1]
    all_information["acs_by_step"]=average_acc_by_step
    all_information["pcs_by_step"]=average_tps_by_step
    all_information["average_pqs"]=average_process_score

    # print(all_information)
    return all_information

def parse_arguments():
    parser = argparse.ArgumentParser(description='ACS/PCS/PQS calculation for different LMMs.')
    parser.add_argument('--model_name', type=str, required=True, help='The model of the calculated metrics')
    parser.add_argument('--input_json', type=str, required=True, help='Directory containing the scored JSON files.')
    parser.add_argument('--output_json', type=str, required=True, help='Directory containing the result JSON files.')
    return parser.parse_args()

# Main entry point 
if __name__ == "__main__":
    args = parse_arguments()
    model=args.model_name
    
    model_information={}
    inputfile_path = args.input_json
    with open(inputfile_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    this_information = count_three_metrics(data,model)
    # print("model",model)
    model_information[f"{model}"]=this_information
    # print("model_information",model_information)
    savefile_path = args.output_json
    with open(savefile_path, 'w', encoding='utf-8') as file:
        json.dump(model_information, file, ensure_ascii=False, indent=4)
    