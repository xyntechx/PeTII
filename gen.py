from dotenv import load_dotenv
from argparse import ArgumentParser
from datetime import datetime
from loguru import logger
from pathlib import Path

from pipeline import pipeline
from utils import read


def ch_no_j(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_b_llm = pipeline.ChP("B", user_interest, reference_text, save_dir)

    # Run whole-chapter Personalization LLM -- draft
    p_b_llm.personalize()


def ch_with_j(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_b_llm = pipeline.ChP("B", user_interest, reference_text, save_dir)
    j_llm = pipeline.Judge(user_interest, reference_text, save_dir)

    # Run whole-chapter Personalization LLM -- draft
    p_b_llm.personalize()

    # Give feedback to whole-chapter Personalization LLM
    j_llm.give_feedback(p_b_llm)

    # Run whole-chapter Personalization LLM -- refinement
    p_b_llm.refine()


def co_no_j(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_a_llm = pipeline.CoP("A", user_interest, reference_text, save_dir)

    # Run content-by-content Personalization LLM -- draft
    p_a_llm.extract_concepts()
    p_a_llm.create_overview()
    p_a_llm.personalize()


def co_with_j(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_a_llm = pipeline.CoP("A", user_interest, reference_text, save_dir)
    j_llm = pipeline.Judge(user_interest, reference_text, save_dir)

    # Run content-by-content Personalization LLM -- draft
    p_a_llm.extract_concepts()
    p_a_llm.create_overview()
    p_a_llm.personalize()

    # Give feedback to content-by-content Personalization LLM
    j_llm.give_feedback(p_a_llm)

    # Run content-by-content Personalization LLM -- refinement
    p_a_llm.refine()


def se_compete(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_a_llm = pipeline.CoP("A", user_interest, reference_text, save_dir)
    p_b_llm = pipeline.ChP("B", user_interest, reference_text, save_dir)
    j_llm = pipeline.Judge(user_interest, reference_text, save_dir)

    # Run content-by-content Personalization LLM -- draft
    p_a_llm.extract_concepts()
    p_a_llm.create_overview()
    p_a_llm.personalize()

    # Give feedback to content-by-content Personalization LLM
    j_llm.give_feedback(p_a_llm)

    # Run whole-chapter Personalization LLM -- draft
    p_b_llm.personalize()

    # Give feedback to whole-chapter Personalization LLM
    j_llm.give_feedback(p_b_llm)

    # Run content-by-content Personalization LLM -- refinement
    p_a_llm.refine()

    # Run whole-chapter Personalization LLM -- refinement
    p_b_llm.refine()

    # Compare refined drafts
    j_llm.compare(p_a_llm, p_b_llm)


def re_compete(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_a_llm = pipeline.CoP("A", user_interest, reference_text, save_dir)
    p_b_llm = pipeline.ChP("B", user_interest, reference_text, save_dir)
    j_llm = pipeline.Judge(user_interest, reference_text, save_dir)

    # Run content-by-content Personalization LLM -- draft
    p_a_llm.extract_concepts()
    p_a_llm.create_overview()
    p_a_llm.personalize()

    # Give feedback to content-by-content Personalization LLM
    j_llm.give_feedback(p_a_llm, PLLM_other=p_b_llm, compete=True)

    # Run whole-chapter Personalization LLM -- draft
    p_b_llm.personalize()

    # Give feedback to whole-chapter Personalization LLM
    j_llm.give_feedback(p_b_llm, PLLM_other=p_a_llm, compete=True)

    # Run content-by-content Personalization LLM -- refinement
    p_a_llm.refine()

    # Run whole-chapter Personalization LLM -- refinement
    p_b_llm.refine()

    # Compare refined drafts
    j_llm.compare(p_a_llm, p_b_llm)


def complete(reference_text:str, user_interest:str, save_dir:str):
    # Initialize LLMs
    p_a_llm = pipeline.CoP("A", user_interest, reference_text, save_dir)
    p_b_llm = pipeline.ChP("B", user_interest, reference_text, save_dir)
    j_llm = pipeline.Judge(user_interest, reference_text, save_dir)

    # Run content-by-content Personalization LLM -- draft
    p_a_llm.extract_concepts()
    p_a_llm.write_outline()
    p_a_llm.create_overview()
    p_a_llm.personalize(with_outline=True)

    # Give feedback to content-by-content Personalization LLM
    j_llm.give_feedback(p_a_llm, PLLM_other=p_b_llm, compete=True)

    # Run whole-chapter Personalization LLM -- draft
    p_b_llm.personalize()

    # Give feedback to whole-chapter Personalization LLM
    j_llm.give_feedback(p_b_llm, PLLM_other=p_a_llm, compete=True)

    # Run content-by-content Personalization LLM -- refinement
    p_a_llm.refine()

    # Run whole-chapter Personalization LLM -- refinement
    p_b_llm.refine()

    # Compare refined drafts
    j_llm.compare(p_a_llm, p_b_llm)


def main(og_chapter_src:str, user_interest:str, strategy_name:str):
    # Get relevant strategy function
    strategy = STRATEGIES[strategy_name]

    # Read original chapter markdown
    reference_text = read(og_chapter_src)

    # Setting logistics
    course_name, chapter_title = og_chapter_src.split("/")[1:3]
    chapter_title = "-".join(chapter_title.split(".")[:-1])
    curr_date = datetime.now()
    save_dir = f"output/{course_name}/{chapter_title}/{curr_date.year}{curr_date.month}{curr_date.day}{curr_date.hour}{curr_date.minute}{curr_date.second}"

    # Document execution strategy
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{save_dir}/strategy.txt", "w", encoding="utf-8") as file:
        file.write(f"Strategy: {strategy_name}")
        logger.info(f"Strategy logged in {save_dir}/strategy.txt")

    strategy(reference_text, user_interest, save_dir)
    logger.success(f"Personalization completed! All work is saved in {save_dir}")


if __name__ == "__main__":
    load_dotenv()

    STRATEGIES = {
        "ch_no_j": ch_no_j, # only whole-chapter personalization, no judge
        "ch_with_j": ch_with_j, # only whole-chapter personalization, with judge
        "co_no_j": co_no_j, # only content-by-content personalization, no judge
        "co_with_j": co_with_j, # only content-by-content personalization, with judge
        "se_compete": se_compete, # both content-by-content and whole-chapter personalization, compete separately
        "re_compete": re_compete, # both content-by-content and whole-chapter personalization, Reinforcement Competition
        "complete": complete # Reinforcement Competition + outline/layout extraction
    }

    parser = ArgumentParser()
    parser.add_argument("-c", "--chapter", dest="chapter", help="The original textbook chapter to personalize", required=True)
    parser.add_argument("-i", "--interest", dest="interest", help="Your personal/professional interest", required=True)
    parser.add_argument("-s", "--strategy", dest="strategy", help="Execution strategy", required=True, choices=list(STRATEGIES.keys()))
    args = parser.parse_args()

    main(args.chapter, args.interest, args.strategy)
