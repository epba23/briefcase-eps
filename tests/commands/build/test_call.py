def test_specific_app(build_command, first_app, second_app):
    "If a specific app is requested, build it"
    # Add two apps
    build_command.apps = {
        'first': first_app,
        'second': second_app,
    }

    # Configure no command line options
    options = build_command.parse_options([])

    # Run the build command
    build_command(first_app, **options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # Build the first app; no state
        ('build', 'first', {'input_enabled': True, 'verbosity': 1}),
    ]


def test_multiple_apps(build_command, first_app, second_app):
    "If there are multiple apps, build all of them"
    # Add two apps
    build_command.apps = {
        'first': first_app,
        'second': second_app,
    }

    # Configure no command line options
    options = build_command.parse_options([])

    # Run the build command
    build_command(**options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # Build the first app; no state
        ('build', 'first', {'input_enabled': True, 'verbosity': 1}),

        # Build the second apps; state from previous build.
        (
            'build',
            'second',
            {'input_enabled': True, 'verbosity': 1, 'build_state': 'first'}
        ),
    ]


def test_non_existent(build_command, first_app_config, second_app):
    "Requesting a build of a non-existent app causes a create"
    # Add two apps; use the "config only" version of the first app.
    build_command.apps = {
        'first': first_app_config,
        'second': second_app,
    }

    # Configure no command line options
    options = build_command.parse_options([])

    # Run the build command
    build_command(**options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # First App doesn't exist, so it will be created, then built
        ('create', 'first', {'input_enabled': True, 'verbosity': 1}),
        (
            'build',
            'first',
            {'input_enabled': True, 'verbosity': 1, 'create_state': 'first'}
        ),

        # Second app *does* exist, so it only be built
        (
            'build',
            'second',
            {
                'input_enabled': True,
                'verbosity': 1,
                'create_state': 'first',
                'build_state': 'first'
            }
        ),
    ]


def test_unbuilt(build_command, first_app_unbuilt, second_app):
    "Requesting a build of an app that has been created, but not build, just causes a build"
    # Add two apps; use the "unbuilt" version of the first app.
    build_command.apps = {
        'first': first_app_unbuilt,
        'second': second_app,
    }

    # Configure no command line options
    options = build_command.parse_options([])

    # Run the build command
    build_command(**options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # First App exists, but hasn't been built; it will be built.
        ('build', 'first', {'input_enabled': True, 'verbosity': 1}),

        # Second app has been built before; it will be built again.
        (
            'build',
            'second',
            {'input_enabled': True, 'verbosity': 1, 'build_state': 'first'}
        ),
    ]


def test_update_app(build_command, first_app, second_app):
    "If an update is requested, app is updated before build"
    # Add two apps
    build_command.apps = {
        'first': first_app,
        'second': second_app,
    }

    # Configure a -a command line option
    options = build_command.parse_options(['-u'])

    # Run the build command
    build_command(**options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # Update then build the first app
        (
            'update',
            'first',
            {'input_enabled': True, 'verbosity': 1}
        ),
        (
            'build',
            'first',
            {'input_enabled': True, 'verbosity': 1, 'update_state': 'first'}
        ),

        # Update then build the second app
        (
            'update',
            'second',
            {
                'input_enabled': True,
                'verbosity': 1,
                'update_state': 'first',
                'build_state': 'first'
            }
        ),
        (
            'build',
            'second',
            {
                'input_enabled': True,
                'verbosity': 1,
                'update_state': 'second',
                'build_state': 'first'
            }
        ),
    ]


def test_update_non_existent(build_command, first_app_config, second_app):
    "Requesting an update of a non-existent app causes a create"
    # Add two apps; use the "config only" version of the first app.
    build_command.apps = {
        'first': first_app_config,
        'second': second_app,
    }

    # Configure no command line options
    options = build_command.parse_options(['-u'])

    # Run the build command
    build_command(**options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # First App doesn't exist, so it will be created, then built
        ('create', 'first', {'input_enabled': True, 'verbosity': 1}),
        (
            'build',
            'first',
            {'input_enabled': True, 'verbosity': 1, 'create_state': 'first'}
        ),

        # Second app *does* exist, so it will be updated, then built
        (
            'update',
            'second',
            {
                'input_enabled': True,
                'verbosity': 1,
                'create_state': 'first',
                'build_state': 'first'
            }
        ),
        ('build', 'second', {
            'input_enabled': True,
            'verbosity': 1,
            'create_state': 'first',
            'build_state': 'first',
            'update_state': 'second'
        }),
    ]


def test_update_unbuilt(build_command, first_app_unbuilt, second_app):
    "Requesting an update of an upbuilt app causes an update before build"
    # Add two apps; use the "unbuilt" version of the first app.
    build_command.apps = {
        'first': first_app_unbuilt,
        'second': second_app,
    }

    # Configure no command line options
    options = build_command.parse_options(['-u'])

    # Run the build command
    build_command(**options)

    # The right sequence of things will be done
    assert build_command.actions == [
        # Tools are verified
        ('verify', {'verbosity': 1, 'input_enabled': True}),

        # First App exists, but hasn't been built; it will updated then built.
        ('update', 'first', {'input_enabled': True, 'verbosity': 1}),
        (
            'build',
            'first',
            {'input_enabled': True, 'verbosity': 1, 'update_state': 'first'}
        ),

        # Second app has been built before; it will be built again.
        (
            'update',
            'second',
            {
                'input_enabled': True,
                'verbosity': 1,
                'update_state': 'first',
                'build_state': 'first'
            }
        ),
        (
            'build',
            'second',
            {
                'input_enabled': True,
                'verbosity': 1,
                'update_state': 'second',
                'build_state': 'first'
            }
        ),
    ]
