from django.conf import settings
from django.contrib import messages
from django_tables2 import SingleTableView
from django.shortcuts import redirect
from django.views.generic import UpdateView, DetailView, CreateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User

from hubcave.game.forms import GameUpdateForm, GameCreateForm
from hubcave.game.models import Game
from hubcave.game.tables import GameTable

# Create your views here.

class GameList(SingleTableView):
    table_class = GameTable
    model = Game

    def get_context_data(self, **kwargs):
        self.queryset = Game.objects.filter(user_id=self.request.user.id)


class GameDetail(DetailView):
    model = Game
    slug_field = 'repository'

    def dispatch(self, request, *args, **kwargs):
        return super(GameDetail, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if getattr(settings, 'SOCKETIO_ENABLED', False):
            print "Sockets are enabled! Go forth and conquer"
            return ['game/game_detail_socketio.html']
        else:
            return ['game/game_detail.html']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GameDetail, self).get_context_data(**kwargs)
        self.object.generate_or_update_map()
        return context

class GameCreate(CreateView):
    model = Game
    form_class = GameCreateForm
    template_name_suffix = '_create'

    def form_valid(self, form):
        """After the form is valid lets let people know"""
        ret = super(GameCreate, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS,
                             "Game for %s/%s created".format(self.object.user,
                                                             self.object.repository))
        return ret

class GameUpdate(UpdateView):
    """
    Update a game
    """
    model = Game
    form_class = GameUpdateForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('game_game_list')
