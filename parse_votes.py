import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict

logger = logging.getLogger(__name__)


def main():
    try:
        bills = "./files/in/bills.csv"
        legislators_csv = "./files/in/legislators.csv"
        votes_csv = "./files/in/votes.csv"
        vote_results_csv = "./files/in/vote_results.csv"

        legislator_summary = _legislator_support_oppose(
            legislators_csv_filename=legislators_csv,
            votes_result_csv_filename=vote_results_csv,
        )

        output_folder = "./files/out"
        output_filename = os.path.join(
            output_folder, "legislators-support-oppose-count.csv"
        )

        _save_dict_of_dicts_to_csv(legislator_summary, output_filename)
        logger.info("Legislator support/oppose count saved to %s", output_filename)

    except Exception as e:
        logger.exception("Exception raised in main: %s.", e)


def _save_dict_of_dicts_to_csv(
    data_to_save: Dict[str, Dict[str, Any]], output_filename: str
):
    """
    Saves a dictionary of dictionaries to a CSV file.
    Each key-value pair in the outer dictionary is not directly used in the CSV structure,
    but the inner dictionaries are treated as rows.

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
    except StopIteration:
        logger.warning(
            "Data to save is empty or not structured as expected (no inner dictionaries to get fieldnames)."
        )
    except IOError as e:
        logger.error(
            "Error writing data to CSV file %s: %s", output_filename, e, exc_info=True
        )
    except Exception as e:
        logger.error(
            "An unexpected error occurred while writing data to CSV %s: %s",
            output_filename,
            e,
            exc_info=True,
        )


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

            if not vote_type_str:
                logger.warning(
                    "Vote result for legislator '%s' (vote result ID '%s') is missing 'vote_type'. Skipping this vote.",
                    legislator_id,
                    vote_result_id,
                )
                continue

            try:
                vote_type = int(vote_type_str)
            except ValueError:
                logger.warning(
                    "Invalid 'vote_type' '%s' for legislator '%s' (vote result ID '%s'). Skipping this vote.",
                    vote_type_str,
                    legislator_id,
                    vote_result_id,
                )
                continue

            if vote_type == 1:  # Yea
                legislators_support_oppose_count[legislator_id][
                    "num_supported_bills"
                ] += 1
            elif vote_type == 2:  # Nay
                legislators_support_oppose_count[legislator_id][
                    "num_opposed_bills"
                ] += 1

        return legislators_support_oppose_count

    except Exception as e:
        raise e


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
        logger.error("Error: The file %s was not found.", filename)
        raise

    except Exception as e:
        logger.exception("An error occurred while parsing %s", filename)
        raise

    return data_dict


if __name__ == "__main__":
    main()
