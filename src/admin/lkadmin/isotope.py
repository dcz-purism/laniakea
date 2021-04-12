# Copyright (C) 2018-2019 Matthias Klumpp <matthias@tenstral.net>
#
# Licensed under the GNU Lesser General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the license, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import sys
from typing import Optional
from laniakea.db import session_scope, ImageBuildRecipe, ImageFormat, LkModule, Job, JobKind
from .utils import print_header, print_done, print_note, input_str, input_list
from laniakea.msgstream import EventEmitter


def add_image_recipe(options):

    print_header('Add new ISO/IMG image build recipe')

    with session_scope() as session:
        recipe = ImageBuildRecipe()

        recipe.distribution = input_str('Name of the distribution to build the image for')
        recipe.suite = input_str('Name of the suite to build the image for')
        recipe.environment = input_str('Environment of the image (e.g. GNOME, Plasma, server, ...)')
        recipe.style = input_str('Style of this OS image (e.g. "oem", "live", ...)')
        recipe.architectures = input_list('List of architectures to build for')
        recipe.host_architecture = input_str(('Architecture of the host that is allowed to build images '
                                              '(put "any" to allow any host)'))

        while True:
            format_str = input_str('Type of image that we are building (iso/img)').lower()
            if format_str == 'iso':
                recipe.format = ImageFormat.ISO
                break
            if format_str == 'img':
                recipe.format = ImageFormat.IMG
                break
            print_note('The selected image format is unknown.')

        recipe.name = input_str('Unique name for this recipe (format will be automatically prefixed)').lower()
        recipe.git_url = input_str('Git repository URL containing the image build configuration')
        recipe.result_move_to = input_str('Place to move the build result to (placeholders like %{DATE} are allowed)')

        # type-prefix recipe name
        recipe.name = '{}:{}'.format(format_str, recipe.name)

        # add recipe to the database
        session.add(recipe)
        session.commit()

        # announce the event
        emitter = EventEmitter(LkModule.ADMINCLI)
        ev_data = {'name': recipe.name,
                   'format': format_str,
                   'architectures': recipe.architectures,
                   'distribution': recipe.distribution,
                   'suite': recipe.suite,
                   'environment': recipe.environment,
                   'style': recipe.style}
        emitter.submit_event_for_mod(LkModule.ISOTOPE,
                                     'recipe-created',
                                     ev_data)

        print_done('Created recipe with name: {}'.format(recipe.name))


def trigger_image_build(options):
    recipe_name = options.trigger_build

    with session_scope() as session:
        recipe: Optional[ImageBuildRecipe] = session.query(ImageBuildRecipe) \
                                                    .filter(ImageBuildRecipe.name == recipe_name).one_or_none()

        if not recipe:
            print_note('Recipe with name "{}" was not found!'.format(recipe_name))
            sys.exit(2)

        emitter = EventEmitter(LkModule.ADMINCLI)

        job_count = 0
        for arch in recipe.architectures:
            job = Job()
            job.module = LkModule.ISOTOPE
            job.kind = JobKind.OS_IMAGE_BUILD
            job.trigger = recipe.uuid
            job.architecture = recipe.host_architecture
            if job.architecture != arch:
                job.data = {'architecture': arch}

            session.add(job)
            session.commit()  # to generate an uuid for this job to announce

            job_count += 1

            # announce the event
            ev_data = {'name': recipe.name,
                       'architecture': arch,
                       'format': str(recipe.format),
                       'distribution': recipe.distribution,
                       'suite': recipe.suite,
                       'environment': recipe.environment,
                       'style': recipe.style,
                       'job_id': str(job.uuid)}
            emitter.submit_event_for_mod(LkModule.ISOTOPE,
                                         'build-job-added',
                                         ev_data)

        session.commit()
        print_done('Scheduled {} job(s) for {}.'.format(job_count, recipe.name))


def module_isotope_init(options):
    ''' Change the Laniakea Isotope module '''

    if options.add_recipe:
        add_image_recipe(options)
    elif options.trigger_build:
        trigger_image_build(options)
    else:
        print('No action selected.')
        sys.exit(1)


def add_cli_parser(parser):
    sp = parser.add_parser('isotope', help='Configure disk image build recipes.')

    sp.add_argument('--add-recipe', action='store_true', dest='add_recipe',
                    help='Create a new image build recipe.')

    sp.add_argument('--trigger-build', dest='trigger_build',
                    help='Schedule a disk image build job.')

    sp.set_defaults(func=module_isotope_init)
