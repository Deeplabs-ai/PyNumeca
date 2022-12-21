import pandas as pd


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def plan_to_dataframe(
        plan_path: str,
        log_head: bool = False
):
    """
    :param plan_path: .plan file path
    :param log_head: logging or not the dataframe head
    :return: pandas dataframe representing the specified .plan file

    Converting a Numeca .plan file into a pandas dataframe.plan

    """

    # Reading the plan file
    with open(plan_path, 'r') as f:
        content = f.read()

    # fixing .plan variable spacing
    for i in range(1, 10):
        content = content.replace(i * ' ', ' ')
    
    content = content.replace('\t', ' ')

    # Reading dataframe columns
    edp = find_between(content, '# Design parameters', '# Responses').replace('\n', '').split()
    responses = find_between(content, '# Responses', '# Experiments ').replace('\n', '').split()
    info = find_between(content, '# Experiments (', ')').replace('\n', '').replace(',', '').split()

    # Reading raw dataframe
    df_raw = [[item for item in line.split(' ') if item != ''] for line in content[content.index(')') + 2:].split('\n')]

    # Merging columns
    cols = info[:2]
    cols.extend(edp)
    cols.extend(responses)
    cols.append(info[-1])

    # Final DataFrame
    df = pd.DataFrame(df_raw, columns=cols)
    print(f'DataFrame shape: ', {df.shape})
    if log_head:
        print(df.head())

    return df