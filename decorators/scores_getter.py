
def scores_getter(function_to_decorate):
    def a_wrapper_accepting_arguments(self, vk, event):
        try:
            scores = int(event.text)
            if scores < 0:
                scores *= -1
            function_to_decorate(self, vk, event, scores)
        except ValueError:
            vk.send(event.user_id, 'ты ввел хуйню какую-то, мне нужно число')

    return a_wrapper_accepting_arguments
