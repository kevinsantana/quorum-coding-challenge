import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(filename)s %(funcName)s %(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)


def main():
    """
    """
    try:
        bills_csv = "./files/in/bills.csv"
        legislators_csv = "./files/in/legislators.csv"
        votes_csv = "./files/in/votes.csv"
        vote_results_csv = "./files/in/vote_results.csv"
        _create_results_and_save_csv(
            bills_csv_filename=bills_csv,
            legislators_csv_filename=legislators_csv,
            votes_csv_filename=votes_csv,
            vote_results_csv_filename=vote_results_csv,
        )

    except Exception as e:
        logger.exception("Exception raised in main: %s.", e)


def _create_results_and_save_csv(
    bills_csv_filename: str,
    legislators_csv_filename: str,
    votes_csv_filename: str,
    vote_results_csv_filename: str,
):
    """
    """
    try:
        legislator_summary = _legislator_support_oppose(
            legislators_csv_filename=legislators_csv_filename,
            votes_result_csv_filename=vote_results_csv_filename,
        )
        output_folder = "./files/out"
        output_filename = os.path.join(
            output_folder, "legislators-support-oppose-count.csv"
        )
        _save_results_to_csv(legislator_summary, output_filename)
        logger.info("Legislator support/oppose count saved to %s", output_filename)
        bill_analysis = _analyze_bill_votes_and_sponsors(
            bills_csv_filename=bills_csv_filename,
            legislators_csv_filename=legislators_csv_filename,
            votes_csv_filename=votes_csv_filename,
            vote_results_csv_filename=vote_results_csv_filename,
        )
        output_bill_analysis_filename = os.path.join(
            output_folder, "bill-vote-sponsor-analysis.csv"
        )
        _save_results_to_csv(bill_analysis, output_bill_analysis_filename)
        logger.info(
            "Bill vote and sponsor analysis saved to %s", output_bill_analysis_filename
        )
    except Exception:
        logger.exception("Exception raised in _create_results_and_save_csv.")
        raise


def _save_results_to_csv(
    data_to_save: Dict[str, Dict[str, Any]], output_filename: str
):
    """
    Saves a dictionary of a CSV file. Each key-value pair in the outer dictionary
    is not directly used in the CSV structure, but the inner dictionaries are
    treated as rows.

    Args:
        data_to_save: A dictionary where each value is another dictionary
                      representing a row in the CSV. All inner dictionaries
                      should ideally have the same set of keys, which will
                      become the CSV headers.
        output_filename: The path to the output CSV file.
    """
    if not data_to_save:
        logger.warning("No data provided to save to CSV.")
        return

    output_dir = os.path.dirname(output_filename)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        fieldnames = list(next(iter(data_to_save.values())).keys())
        with open(output_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row_dict in data_to_save.values():
                writer.writerow(row_dict)

    except Exception:
        logger.exception(
            "An unexpected error occurred while writing data to CSV %s",
            output_filename,
        )
        raise


def _legislator_support_oppose(
    legislators_csv_filename: str, votes_result_csv_filename: str
) -> Dict[str, Dict[str, Any]]:
    """
    Calculates the number of bills each legislator supported (voted Yea) and
    opposed (voted Nay) based on the vote_results.csv file.

    Returns:
        A dictionary where keys are legislator IDs and values are dictionaries
        containing legislator's name, number of supported bills, and number of
        opposed bills.
        e.g., {
            "legislator_id_1": {
                "id": "legislator_id_1",
                "name": "Legislator Name One",
                "num_supported_bills": 10,
                "num_opposed_bills": 5
            }, ...
        }
    """

    try:
        legislators_data = _parse_csv(filename=legislators_csv_filename)
        vote_results_data = _parse_csv(filename=votes_result_csv_filename)
        legislators_support_oppose_count = defaultdict(dict)

        for vote_result_id, vote_info in vote_results_data.items():
            legislator_id = vote_info.get("legislator_id")
            vote_type_str = vote_info.get("vote_type")

            if not legislator_id:
                logger.warning(
                    "Vote result entry with ID '%s' is missing 'legislator_id'. Skipping.",
                    vote_result_id,
                )
                continue

            if legislator_id not in legislators_support_oppose_count:
                legislator_details = legislators_data.get(legislator_id)
                if legislator_details:
                    legislators_support_oppose_count[legislator_id][
                        "id"
                    ] = legislator_id
                    legislators_support_oppose_count[legislator_id]["name"] = (
                        legislator_details.get("name", "Unknown Name")
                    )
                    legislators_support_oppose_count[legislator_id][
                        "num_supported_bills"
                    ] = 0
                    legislators_support_oppose_count[legislator_id][
                        "num_opposed_bills"
                    ] = 0
                else:
                    logger.warning(
                        "Legislator with ID '%s' not found in legislators data. Votes will be counted, but name will be 'Unknown Legislator'.",
                        legislator_id,
                    )
                    legislators_support_oppose_count[legislator_id][
                        "id"
                    ] = legislator_id
                    legislators_support_oppose_count[legislator_id][
                        "name"
                    ] = "Unknown Legislator"
                    legislators_support_oppose_count[legislator_id][
                        "num_supported_bills"
                    ] = 0
                    legislators_support_oppose_count[legislator_id][
                        "num_opposed_bills"
                    ] = 0
            vote_type = int(vote_type_str)
            if vote_type == 1:  # Yea
                legislators_support_oppose_count[legislator_id][
                    "num_supported_bills"
                ] += 1
            elif vote_type == 2:  # Nay
                legislators_support_oppose_count[legislator_id][
                    "num_opposed_bills"
                ] += 1

        return legislators_support_oppose_count

    except Exception:
        logger.error(
            "Error during legislator support/oppose count calculation: %s", e, exc_info=True
        )
        raise


def _analyze_bill_votes_and_sponsors(
    bills_csv_filename: str,
    legislators_csv_filename: str,
    votes_csv_filename: str,
    vote_results_csv_filename: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Analyzes each bill to count legislator support and opposition,
    and identifies the primary sponsor.

    Args:
        bills_csv_filename: Path to the bills CSV file.
        legislators_csv_filename: Path to the legislators CSV file.
        votes_csv_filename: Path to the votes CSV file.
        vote_results_csv_filename: Path to the vote_results CSV file.

    Returns:
        A dictionary where keys are bill IDs. Each value is a dictionary
        containing bill_id, title, supporter_count, opposer_count,
        and primary_sponsor_name.
    """
    try:
        bills_data = _parse_csv(filename=bills_csv_filename)
        legislators_data = _parse_csv(filename=legislators_csv_filename)
        votes_data = _parse_csv(filename=votes_csv_filename)
        vote_results_data = _parse_csv(filename=vote_results_csv_filename)
        bill_analysis_results = {}

        for bill_id, bill_info in bills_data.items():
            sponsor_id = bill_info.get("sponsor_id")
            sponsor_name = "Unknown Sponsor"
            if sponsor_id:
                sponsor_details = legislators_data.get(sponsor_id)
                if sponsor_details:
                    sponsor_name = sponsor_details.get("name", "Unnamed Sponsor")
                else:
                    logger.warning(
                        "Sponsor ID '%s' for bill '%s' not found in legislators data.",
                        sponsor_id,
                        bill_id,
                    )

            bill_analysis_results[bill_id] = {
                "id": bill_id,
                "title": bill_info.get("title", "No Title Provided"),
                "supporter_count": 0,
                "opposer_count": 0,
                "primary_sponsor_name": sponsor_name,
            }

        for vr_id, vote_result_info in vote_results_data.items():
            vote_id = vote_result_info.get("vote_id")
            vote_type_str = vote_result_info.get("vote_type")

            if (
                not vote_id
                or not (vote_details := votes_data.get(vote_id))
                or not (bill_id := vote_details.get("bill_id"))
            ):
                logger.warning(
                    "Could not link vote result '%s' to a bill. Skipping.", vr_id
                )
                continue

            if bill_id not in bill_analysis_results:
                logger.warning(
                    "Bill ID '%s' (from vote '%s') not found in the initial bill list. This vote will not be counted.",
                    bill_id,
                    vote_id,
                )
                continue

            if vote_type_str and vote_type_str.isdigit():
                vote_type = int(vote_type_str)
                if vote_type == 1:  # Yea
                    bill_analysis_results[bill_id]["supporter_count"] += 1
                elif vote_type == 2:  # Nay
                    bill_analysis_results[bill_id]["opposer_count"] += 1
        return bill_analysis_results

    except Exception:
        logger.exception("Error during bill votes and sponsors analysis.")
        raise


def _parse_csv(filename: str) -> Dict[str, Dict[str, Any]] | Dict:
    """
    Parses a CSV file and converts it into a dictionary.

    The keys of the main dictionary are taken from the first column of the CSV.
    The values are dictionaries representing each row, where keys are column headers.

    Args:
        file_path: The absolute path to the CSV file.

    Returns:
        A dictionary representing the CSV data, keyed by the first column's values.
    """
    data_dict = {}
    try:
        with open(filename, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames:
                logger.warning("CSV file %s is empty or has no headers.", filename)
                return data_dict

            # Assuming the first column header is the key for the outer dictionary
            # e.g. 'id'
            primary_key_column = reader.fieldnames[0]

            for row in reader:
                key = row.get(primary_key_column)
                if key is None:
                    logger.warning(
                        "Row in %s is missing primary key '%s': %s. Skipping row.",
                        filename,
                        primary_key_column,
                        row,
                    )
                    continue
                data_dict[key] = row

    except FileNotFoundError:
        logger.exception("Error: The file %s was not found.", filename)
        raise

    except Exception:
        logger.exception("An error occurred while parsing %s", filename)
        raise

    return data_dict


if __name__ == "__main__":
    main()
