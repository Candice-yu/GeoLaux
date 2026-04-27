# GeoLaux: A Benchmark for Evaluating MLLMs' Geometry Performance on Long-Step Problems Requiring Auxiliary Lines

## 💥 News 💥
**[2026.04.06]** GeoLaux is accepted by ACL2026-main!🎉

**[2026.03.01]** We release the English version and the numerical perturbation version of GeoLaux-mini.

**[2025.08.08]** Our paper is now accessible at https://arxiv.org/abs/2508.06226.

## 📚GeoLaux Dataset

GeoLaux is a challenging plane geometry dataset with 2,186 problems. It demonstrates three key advantages over comparable datasets: **(1) Long Steps:** With solutions reaching up to 24 steps, far exceeding previous benchmarks' maximum of 11 steps, GeoLaux poses significant challenges for models. **(2)** **Unique Auxiliary Line Annotation:** To the best of our knowledge, GeoLaux is the first and only benchmark to provide complete, explicit annotations for auxiliary line construction methods in geometry problems, addressing a critical gap in prior work. **(3) Integrated Calculation and Proving Problems:** GeoLaux comprises 1,418 calculation and 768 proving problems.

<img src="assets/dataset_distribution.jpg" alt="image-20250804211123227" style="zoom: 100%;" />

<div align="center">
<p>The step length and auxiliary lines distribution of GeoLaux</p>
</div>

we have placed GeoLaux-mini in the "data" folder, which contains 330 questions uniformly sampled from GeoLaux.

## 🚀 Evaluation Pipeline

![five_dimension_framework](assets/five_dimension_framework.png)

<div align="center">
<p>Five-dimension evaluation framework of GeoLaux. Given golden answer and solution from dataset, evaluator assesses MLLM outputs for answer correctness, step-by-step scoring, and error analysis, enabling framework's comprehensive evaluation across: ① answer correctness, ② process correctness, ③ process quality, ④ auxiliary line impact, and ⑤ error type.</p>
</div>


### 📜Solution Generation

First, obtain the MLLM's problem-solving process on GeoLaux. We take the approach for obtaining closed-source large models as an example.

```bash
cd evaluation
python closedsource_get_ans.py \
    --model_name YourModel \
    --output_json ../answers/YourModel.json 
```

### ✒️Evaluator Analysis

After obtaining the large model's reasoning process, the resulting JSON data is sequentially fed into the evaluator for step-by-step scoring. Here, our default evaluator is o4-mini.

```bash
cd evaluation
python evaluate_score.py \
    --model_name YourModel \
    --input_json ../answers/YourModel.json \
    --output_json ../scores/YourModel.json
```

The step-by-step scores are then input into the evaluator to analyze the error types in incorrect steps.

```bash
cd evaluation
python evaluate_error_type.py \
    --model_name YourModel \
    --input_json ../scores/YourModel.json \
    --output_json ../errors/YourModel.json
```

### 📈Metric Calculation

After obtaining the step-by-step scores, we can calculate the model's ACS and PCS across four step-length categories - along with the average ACS, PCS, and PQS - using the three_metrics.py script to compare with the results reported in the paper.

```bash
cd evaluation
python three_metrics.py \
    --model_name YourModel \
    --input_json ../scores/YourModel.json \
    --output_json ../metric/YourModel.json
```

### 📌Note!

Please remenber to replace your openai key in "closedsource_get_ans.py", "evaluate_score.py" and "evaluate_error_type.py".

```python
client = OpenAI(
    base_url="replace_with_your_base_url",
    api_key="replace_with_your_key"
)
```



## 📊Experimental Results

### 📍Model's performance on GeoLaux.

<table>
  <thead>
    <tr>
      <th rowspan="2" style="text-align: center;">Model</th>
      <th colspan="2" style="text-align: center;">1 – 4 Steps</th>
      <th colspan="2" style="text-align: center;">5 – 8 Steps</th>
      <th colspan="2" style="text-align: center;">9 – 12 Steps</th>
      <th colspan="2" style="text-align: center;">13 – 24 Steps</th>
      <th colspan="1" style="text-align: center;">Step-wise</th>
      <th colspan="3" style="text-align: center;">Overall AVG</th>
    </tr>
    <tr>
      <th>ACS</th>
      <th>PCS</th>
      <th>ACS</th>
      <th>PCS</th>
      <th>ACS</th>
      <th>PCS</th>
      <th>ACS</th>
      <th>PCS</th>
      <th>ΔPCS(%)</th>
      <th>ACS</th>
      <th>PCS</th>
      <th>PQS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="13" style="text-align: center;"><b>Thinking MLLMs</b></td>
    </tr>
    <tr>
      <td>QvQ-72B</td>
      <td>69.6</td>
      <td>22.4</td>
      <td>52.7</td>
      <td>6.6</td>
      <td>27.4</td>
      <td>1.7</td>
      <td>14.0</td>
      <td>1.2</td>
      <td>94.6</td>
      <td>52.1</td>
      <td>11.4</td>
      <td>21.0</td>
    </tr>
    <tr>
      <td>o3-mini</td>
      <td>60.7</td>
      <td>21.8</td>
      <td>54.7</td>
      <td>13.0</td>
      <td>39.7</td>
      <td>12.7</td>
      <td>16.5</td>
      <td>5.5</td>
      <td>74.8</td>
      <td>51.8</td>
      <td>15.7</td>
      <td>27.2</td>
    </tr>
    <tr>
      <td>GLM-4.1V-9B-T*</td>
      <td>91.1</td>
      <td>71.0</td>
      <td>78.6</td>
      <td>44.3</td>
      <td>68.3</td>
      <td>31.7</td>
      <td>35.7</td>
      <td>10.7</td>
      <td>84.9</td>
      <td>75.8</td>
      <td>42.8</td>
      <td>57.5</td>
    </tr>
    <tr>
      <td>o1</td>
      <td>86.3</td>
      <td>64.5</td>
      <td>80.9</td>
      <td>57.3</td>
      <td>82.9</td>
      <td>61.0</td>
      <td>42.9</td>
      <td>35.7</td>
      <td>44.7</td>
      <td>79.7</td>
      <td>58.8</td>
      <td>68.6</td>
    </tr>
    <tr>
      <td>Gemini-2.0-T*</td>
      <td>89.7</td>
      <td>72.2</td>
      <td>81.6</td>
      <td>53.4</td>
      <td>64.7</td>
      <td>34.9</td>
      <td>40.2</td>
      <td>17.7</td>
      <td>75.5</td>
      <td>78.7</td>
      <td>54.9</td>
      <td>72.9</td>
    </tr>
    <tr>
      <td>Claude-4.5-T*</td>
      <td>89.3</td>
      <td>69.8</td>
      <td>84.6</td>
      <td>52.5</td>
      <td>71.2</td>
      <td>46.2</td>
      <td>51.2</td>
      <td>33.5</td>
      <td>52.0</td>
      <td>81.7</td>
      <td>56.5</td>
      <td>73.2</td>
    </tr>
    <tr>
      <td>o4-mini</td>
      <td>94.5</td>
      <td>78.3</td>
      <td style="background-color: #d9e8f5;">94.0</td>
      <td>70.3</td>
      <td>91.4</td>
      <td>70.2</td>
      <td style="background-color: #d9e8f5;">81.1</td>
      <td style="background-color: #d9e8f5;">63.4</td>
      <td style="background-color: #d9e8f5;">19.0</td>
      <td style="background-color: #d9e8f5;">92.8</td>
      <td>72.9</td>
      <td>81.1</td>
    </tr>
    <tr>
      <td>Qwen3-VL-32B-T*</td>
      <td>94.9</td>
      <td style="background-color: #d9e8f5;">86.2</td>
      <td>92.8</td>
      <td>74.4</td>
      <td>84.9</td>
      <td>66.4</td>
      <td>64.0</td>
      <td>48.8</td>
      <td>43.4</td>
      <td>90.3</td>
      <td>75.7</td>
      <td>84.2</td>
    </tr>
    <tr>
      <td>o3</td>
      <td>94.4</td>
      <td>83.9</td>
      <td>93.9</td>
      <td style="background-color: #d9e8f5;">80.9</td>
      <td style="background-color: #d9e8f5;">92.7</td>
      <td>73.2</td>
      <td>78.6</td>
      <td>53.6</td>
      <td>36.1</td>
      <td>92.4</td>
      <td style="background-color: #d9e8f5;">78.5</td>
      <td>86.0</td>
    </tr>
    <tr>
      <td>Gemini-2.5-Pro</td>
      <td style="background-color: #d9e8f5;">95.3</td>
      <td>85.9</td>
      <td>92.2</td>
      <td>76.2</td>
      <td>88.0</td>
      <td style="background-color: #d9e8f5;">76.0</td>
      <td>71.3</td>
      <td>50.0</td>
      <td>41.8</td>
      <td>91.2</td>
      <td>77.8</td>
      <td style="background-color: #d9e8f5;">88.6</td>
    </tr>
    <tr>
      <td colspan="13" style="text-align: center;"><b>Non-Thinking MLLMs</b></td>
    </tr>
    <tr>
      <td>Qwen2.5-VL-7B</td>
      <td>38.7</td>
      <td>8.5</td>
      <td>23.6</td>
      <td>1.2</td>
      <td>12.3</td>
      <td>0.0</td>
      <td>8.5</td>
      <td>0.0</td>
      <td>100.0</td>
      <td>26.4</td>
      <td>3.7</td>
      <td>11.1</td>
    </tr>
    <tr>
      <td>GPT-4o</td>
      <td>57.7</td>
      <td>14.7</td>
      <td>49.4</td>
      <td>2.8</td>
      <td>28.1</td>
      <td>0.3</td>
      <td>10.4</td>
      <td>0.6</td>
      <td>95.9</td>
      <td>46.1</td>
      <td>6.7</td>
      <td>20.4</td>
    </tr>
    <tr>
      <td>InternVL3-8B</td>
      <td>72.8</td>
      <td>30.2</td>
      <td>50.2</td>
      <td>7.7</td>
      <td>25.0</td>
      <td>0.6</td>
      <td>10.4</td>
      <td>0.3</td>
      <td>99.0</td>
      <td>51.6</td>
      <td>14.5</td>
      <td>24.9</td>
    </tr>
    <tr>
      <td>GLM-4.1V-9B</td>
      <td>69.2</td>
      <td>31.8</td>
      <td>43.4</td>
      <td>8.1</td>
      <td>20.2</td>
      <td>1.0</td>
      <td>9.1</td>
      <td>0.0</td>
      <td>100.0</td>
      <td>46.8</td>
      <td>15.4</td>
      <td>26.1</td>
    </tr>
    <tr>
      <td>InternVL3.5-8B</td>
      <td>76.2</td>
      <td>33.0</td>
      <td>51.5</td>
      <td>8.2</td>
      <td>27.7</td>
      <td>0.7</td>
      <td>9.8</td>
      <td>0.0</td>
      <td>100.0</td>
      <td>54.0</td>
      <td>15.8</td>
      <td>27.7</td>
    </tr>
    <tr>
      <td>InternVL3-78B</td>
      <td>78.9</td>
      <td>37.6</td>
      <td>60.2</td>
      <td>11.0</td>
      <td>34.2</td>
      <td>4.1</td>
      <td>14.0</td>
      <td>0.6</td>
      <td>98.4</td>
      <td>59.6</td>
      <td>19.1</td>
      <td>34.3</td>
    </tr>
    <tr>
      <td>InternVL3.5-38B</td>
      <td>79.4</td>
      <td>40.7</td>
      <td>56.7</td>
      <td>12.0</td>
      <td>27.1</td>
      <td>0.7</td>
      <td>10.4</td>
      <td>0.0</td>
      <td>100.0</td>
      <td>57.0</td>
      <td>20.2</td>
      <td>34.7</td>
    </tr>
    <tr>
      <td>Claude-3.7</td>
      <td>68.5</td>
      <td>21.0</td>
      <td>55.4</td>
      <td>6.6</td>
      <td>30.1</td>
      <td>2.1</td>
      <td>14.0</td>
      <td>1.8</td>
      <td>91.4</td>
      <td>53.1</td>
      <td>10.9</td>
      <td>35.4</td>
    </tr>
    <tr>
      <td>Claude-4.5</td>
      <td>70.1</td>
      <td>21.0</td>
      <td>61.2</td>
      <td>10.8</td>
      <td>40.4</td>
      <td>6.5</td>
      <td>17.1</td>
      <td>3.0</td>
      <td>85.7</td>
      <td>57.6</td>
      <td>13.3</td>
      <td>36.4</td>
    </tr>
    <tr>
      <td>Claude-4</td>
      <td>67.9</td>
      <td>22.5</td>
      <td>60.6</td>
      <td>10.7</td>
      <td>39.7</td>
      <td>6.2</td>
      <td>17.7</td>
      <td>2.4</td>
      <td>89.3</td>
      <td>56.6</td>
      <td>13.8</td>
      <td>36.6</td>
    </tr>
    <tr>
      <td>GPT-4.1</td>
      <td>70.2</td>
      <td>22.2</td>
      <td>61.0</td>
      <td>9.9</td>
      <td>40.1</td>
      <td>5.8</td>
      <td>18.9</td>
      <td>4.3</td>
      <td>80.6</td>
      <td>57.8</td>
      <td>13.4</td>
      <td>36.3</td>
    </tr>
    <tr>
      <td>Qwen2.5-VL-72B</td>
      <td>77.5</td>
      <td>39.5</td>
      <td>59.5</td>
      <td>14.1</td>
      <td>30.5</td>
      <td>0.7</td>
      <td>16.5</td>
      <td>1.2</td>
      <td>97.0</td>
      <td>58.4</td>
      <td>20.6</td>
      <td>37.3</td>
    </tr>
    <tr>
      <td>Qwen3-VL-32B</td>
      <td style="background-color: #dcf0e2;">92.0</td>
      <td style="background-color: #dcf0e2;">69.9</td>
      <td style="background-color: #dcf0e2;">84.9</td>
      <td style="background-color: #dcf0e2;">48.5</td>
      <td style="background-color: #dcf0e2;">74.3</td>
      <td style="background-color: #dcf0e2;">31.8</td>
      <td style="background-color: #dcf0e2;">55.5</td>
      <td style="background-color: #dcf0e2;">20.1</td>
      <td style="background-color: #dcf0e2;">71.2</td>
      <td style="background-color: #dcf0e2;">83.7</td>
      <td style="background-color: #dcf0e2;">51.9</td>
      <td style="background-color: #dcf0e2;">73.6</td>
    </tr>
  </tbody>
</table>

Table 4: Model's performance on GeoLaux. ACS = Answer Correctness Score, PCS = Process Correctness Score, PQS = Process Quality Score. ΔPCS = ( PCS<sub>1-4Steps</sub> - PCS<sub>13-24Steps</sub> ) / PCS<sub>1-4Steps</sub>, measures performance drop as steps increase. The “T*” in the table is an abbreviation for “Thinking” in the full model name.

**Our analysis reveals three critical findings:**

1. **MLLM performance degrades significantly on long-step problems compared to shorter ones:** Nine models show a performance drop of over 50%  from short-step to ultra-long-step problems, with some exceeding 90% or even reaching 100%.
2. **MLLMs lack the awareness and capability to proactively construct auxiliary lines:** They fail to recognize when such constructions are necessary and struggle to generate correct lines when attempted. Yet, their strong performance gains under standard construction prompting underscore the vital role of accurate auxiliary lines.
3. **MLLMs perform better with limited answer hints, but decline when answers are clearly disclosed:** Compared to free-response problems, models often achieve higher process correctness scores on multiple-choice questions, yet lower on proving problems. This implies options act as incentives for reasoning, while explicit answers lead models to disregard process correctness.

## 🔖 License

Our dataset and code are distributed under the [MIT](LICENSE) license.

## 📖 Citation

If you find GeoLaux useful for your research and applications, please kindly cite our paper:

```bibtex
@article{fu2025geolaux,
  title={GeoLaux: A Benchmark for Evaluating MLLMs' Geometry Performance on Long-Step Problems Requiring Auxiliary Lines},
  author={Fu, Yumeng and Zhu, Jiayin and Zhang, Lingling and Zhao, Bo and Ma, Shaoxuan and Zhang, Yushun and Wu, Yanrui and Wu, Wenjun},
  journal={arXiv preprint arXiv:2508.06226},
  year={2025}
}
```

---

<div align="center">
<sub>⭐ If you find this project useful, please consider giving it a star! ⭐</sub>
</div>

