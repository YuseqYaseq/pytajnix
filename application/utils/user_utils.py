def get_redirection_for_user(user):
    if hasattr(user, 'participant'):
        print('participant')
        return 'application:user_panel'
    elif hasattr(user, 'lecturer'):
        print('lecturer')
        return 'application:lecturer_panel'
    elif hasattr(user, 'moderator'):
        print('moderator')
        return 'application:mod_panel'
    else:
        return 'application:home'
