
def id_getter(function_to_decorate):
    def a_wrapper_accepting_arguments(self, vk, event, user):
        try:
            user_id = int(event.text.replace('id', ''))
            function_to_decorate(self, vk, event, user, user_id)
        except ValueError:
            vk.send(event.user_id, 'ты ввел id не в том формате')

    return a_wrapper_accepting_arguments
