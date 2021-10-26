# GNOME Image Viewer (EOG) Plugin - Sort by Modified Date
# Copyright (C) 2021  Andres Hernandez <cybereality@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from gi.repository import GObject, Gio, Gtk, PeasGtk, Eog
from os import getenv, path

class SortByModifiedPlugin(GObject.Object, Eog.WindowActivatable, PeasGtk.Configurable):
	window = GObject.property(type=Eog.Window)
	CONFIG = "org.gnome.eog.plugins.modified-date"
	
	def __init__(self):
		GObject.Object.__init__(self)
		self.plugin_dir = None
		self.store = None
		self.settings = self.get_settings()
		self.settings.set_boolean("changed", False)
		
	def do_activate(self):
		self.map_event_id = self.window.connect("map-event", self.on_window_event, self)
		self.state_event_id = self.window.connect("window-state-event", self.on_window_event, self)

	def do_deactivate(self):
		self.window.disconnect(self.map_event_id)
		self.window.disconnect(self.state_event_id)
		if self.store:
			self.store.set_default_sort_func(self.sort_name_alphabetic)

	def do_create_configure_widget(self):
		config_ui = Gtk.Builder()
		config_ui_file = self.plugin_dir + "/modified-date.glade"
		if not path.exists(config_ui_file):
			print("Preferences Widget \"" + config_ui_file + "\" Not Found")
			return Gtk.VBox()
		config_ui.add_from_file(config_ui_file)
		toggle_button = config_ui.get_object("reverse")
		toggle_button.connect("toggled", self.on_reverse_toggle)
		reverse = self.settings.get_boolean("reverse")
		toggle_button.set_active(reverse)
		return toggle_button
			
	def get_settings(self):
		data_home = getenv("XDG_DATA_HOME", getenv("HOME") + "/.local/share")
		self.plugin_dir = data_home + "/eog/plugins/modified-date"
		if not path.exists(self.plugin_dir):
			print("Plugin Directory \"" + self.plugin_dir + "\" Not Found")
			return self.SettingsFallback()
		try:
			schema_source = Gio.SettingsSchemaSource.new_from_directory(
				self.plugin_dir,
				Gio.SettingsSchemaSource.get_default(),
				False,)
		except:
			print("Failed to Load Config from \"" + self.plugin_dir + "\"")
			return self.SettingsFallback()
		schema = schema_source.lookup(self.CONFIG, False)
		return Gio.Settings.new_full(schema, None, None)
	
	def on_reverse_toggle(self, toggle):
		self.settings.set_boolean("reverse", toggle.get_active())
		self.settings.set_boolean("changed", True)
	
	def check_for_change(self):
		new_store = self.window.get_store()
		changed = self.settings.get_boolean("changed")
		if self.store is not new_store or changed:
			self.store = new_store
			self.change_sort_order()
			self.settings.set_boolean("changed", False)
	
	def change_sort_order(self):
		reverse = self.settings.get_boolean("reverse")
		if reverse:
			self.store.set_default_sort_func(self.sort_date_descending)
		else:
			self.store.set_default_sort_func(self.sort_date_ascending)
			
	@staticmethod
	def on_window_event(window, event, self):
		self.check_for_change()
	
	@staticmethod
	def sort_date_ascending(store, first, second, data):
		file_1 = store.get_value(first, 2).get_file().get_path()
		file_2 = store.get_value(second, 2).get_file().get_path()
		date_1 = path.getmtime(file_1)
		date_2 = path.getmtime(file_2)

		return (date_1 > date_2) - (date_1 < date_2)
			
	@staticmethod
	def sort_date_descending(store, first, second, data):
		file_1 = store.get_value(first, 2).get_file().get_path()
		file_2 = store.get_value(second, 2).get_file().get_path()
		date_1 = path.getmtime(file_1)
		date_2 = path.getmtime(file_2)

		return (date_2 > date_1) - (date_2 < date_1)
			
	@staticmethod
	def sort_name_alphabetic(store, first, second, data):
		name_1 = store.get_value(first, 2).get_file().get_path().lower()
		name_2 = store.get_value(second, 2).get_file().get_path().lower()

		return (name_1 > name_2) - (name_1 < name_2)
	
	class SettingsFallback():
		def __init__(self):
			self.settings = { "reverse" : False, "changed" : False }
			
		def get_boolean(self, key):
			return self.settings[key]
			
		def set_boolean(self, key, value):
			self.settings[key] = value
			
			
			
			
