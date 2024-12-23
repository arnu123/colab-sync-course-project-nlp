from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.append('../')
import argparse
from utils.cafie_model import ScoringAlgo

parser = argparse.ArgumentParser(description="")

#Specify model name and hyperparameters
parser.add_argument(
    "--alp",
    default=0.99
)
parser.add_argument(
    "--lmd",
    default=100
)
parser.add_argument(
    "--model_name",
    default="gpt2"
)

args = parser.parse_args()
model = AutoModelForCausalLM.from_pretrained(args.model_name, device_map='auto')
tokenizer = AutoTokenizer.from_pretrained(args.model_name, add_prefix_space=True)

tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

list_1_words = []
list_2_words = []
list_3_words = []
word_path = "data\word_lists\list_1.txt" #Path to the word list 1
with open(word_path, "r") as f:
    for line in f:
        list_1_words.append(line[:-1])
word_path = "data\word_lists\list_2.txt" #Path to the word list 2
with open(word_path, "r") as f:
    for line in f:
        list_2_words.append(line[:-1])
word_path = "data\word_lists\list_3.txt" #Path to the word list 3
with open(word_path, "r") as f:
    for line in f:
        list_3_words.append(line[:-1])

def generator(prompt, max_new_tokens=10):
    try:
        runner = ScoringAlgo(
            mdl=model,
            model_name_path='g',
            tokenizer=tokenizer,
            _do_sdb=False, #add sdb prefix to the sentence
            ratio=0.5, #0.5 for avg
            scoring_function="tanh", #Other options- avg, jpdf, arctan, weight
            threshold=0, #bias threshold for scoring
            lmbda=int(args.lmd), #when using scoring, hyperparamenter for scoring function (increasing it increses debiasing but reduces LM score)
            alpha_ratio=float(args.alp), #new probs = alpha*debiased_probs + (1-alpha)*vanilla_probs
            softmax_temperature=1, #temperature for vanilla_probs in alpha
            prompt=prompt,
            context="",
            l1=list_1_words,
            l2=list_2_words,
            l3=list_3_words,
            sent_len=max_new_tokens,
            batch_size=1,
            max_seq_length=128,
            bias_type=None,
            words_to_ignore = []
        )
        _, _, gen_sent, _ = runner()
    except:
        gen_sent = prompt
        print("Error in generation")
    return gen_sent

prompt = "Two boys start a" #prompt for generation
print(generator(prompt))
