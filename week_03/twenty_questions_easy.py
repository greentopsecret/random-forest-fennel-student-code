
import json

def is_answer(node):
    return len(node) == 1

def main():
    f = open('/Users/maxim/codebase/python/spiced_projects/random-forest-fennel-student-code/week_03/questions.json')
    content = f.read()
    node = json.loads(content)

    finished = False

    while not finished:
        print(node['text'])
        if is_answer(node):
            finished = True
        else:
            answer = input()
            if answer.lower() in ['yes', 'y']:
                node = node['yes']
            else:
                node = node['no']

if __name__ == '__main__':
    main()