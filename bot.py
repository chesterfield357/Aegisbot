# Version 0.01 du bot discord
# Test des fonctions, premier jet, juste répondre à la commande !ping

# FAIRE LE TAG DES ROLES, TESTER LE BOT EN EXTERNE, HEBERGER LE BOT ET TESTER SUR LE SERVEUR TEST
# FAIRE LE FORMULAIRE POUR LES PUSH

import os # Import pour utiliser l'environnement
import discord # Module discord
from discord.ext import commands
from discord import ui, app_commands, interactions
from dotenv import load_dotenv # Module pour utiliser les variable d'environnement
from datetime import datetime
import requests
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
RAID_HELPER_TOKEN = os.getenv('RAID_HELPER_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

print("Lancement du bot...")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
   print("Bot allumé !")
   #Synchronisation des commandes 
   try:
      #Sync
      synced = await bot.tree.sync()
      print(f"Commandes slash synchronisées: {len(synced)}")
   except Exception as e:
      print(e)

# Création de l'objet Formulaire
class Questionnaire(ui.Modal, title="Création d'un event donjon"):
    options = [
            discord.SelectOption(label="Become an admin", emoji="👮"),
            discord.SelectOption(
                label="A script problem", value="script", emoji="📜"),
            discord.SelectOption(
                label="Other ...", value="Other", emoji="🤔")
        ]
    key_level = ui.TextInput(label='Quel niveau de clé veux tu faire ?', placeholder="10", min_length=1, max_length=2)
    donjon = ui.Select(placeholder="Catégorie du ticket", options=options, custom_id="category_select", min_values=1, max_values=1,)
    answer2 = ui.TextInput(label='Quel donjon voulez vous faire ?', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Ton event à été créé, n'oublie pas de t'inscrire !", ephemeral=True)

# class Donjon_Bouton(ui.Button, label="Donjon"):
#    async def callback(self, interaction):
#       await super().callback(interaction.response.send_modal(Questionnaire()))
   
class MyView(discord.ui.View):
    @discord.ui.button(label='Donjon', style=discord.ButtonStyle.red)
    async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(Completion())


class Donjon_Select(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        # Define select options
        options = [
            discord.SelectOption(label="Push une clé spécifique", emoji="🎯", value="push"),
            discord.SelectOption(label="Key completion", emoji="📈", value="completion"),
        ]

        # Create and add the select menu
        select = discord.ui.Select(
            placeholder="Selectionne ce que tu souhaite faire",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="category_select"
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_value = interaction.data["values"][0]
        if selected_value == "completion":
            await interaction.response.send_modal(Completion())
            await interaction.edit_original_response(view=Donjon_Select())
        else:
            await interaction.response.send_message(f"Désolé, ce formulaire est encore en developpement", ephemeral=True)

class Completion(discord.ui.Modal, title="📈 Key completion"):
    def __init__(self):
        super().__init__()

        self.short_1 = discord.ui.TextInput(
            custom_id="short_1",
            label="Niveau de la clé à faire ?",
            min_length=1,
            max_length=2,
            placeholder="ex: 12",
            required=True,
        )
        self.add_item(self.short_1)

        self.short_2 = discord.ui.TextInput(
            custom_id="short_2",
            label="Quel jour tu veux jouer ?",
            min_length=5,
            max_length=5,
            placeholder="ex: 10/03",
            required=False,
        )
        self.add_item(self.short_2)

        self.short_3 = discord.ui.TextInput(
            custom_id="short_3",
            label="A quelle heure ?",
            min_length=5,
            max_length=5,
            placeholder="ex: 21h00",
            required=False,
        )
        self.add_item(self.short_3)

        self.add_item(discord.ui.Label(
            text="Quel(s) rôle(s) tu veux tag ?",
            component=discord.ui.Select(
                custom_id="menu_1",
                placeholder="Selectionne un ou plusieurs rôles",
                min_values = 1,
                max_values = 3,
                options = [
                    discord.SelectOption(label="Tank", value="1467532873950171220"),
                    discord.SelectOption(label="Heal", value="1467532901703745608"),
                    discord.SelectOption(label="DPS", value="1467532934402543699"),
                ],
            ),
        ))

    async def tester_format_heure_date(self, tested_value: str):
        value_1_str, value_2_str = tested_value[:2], tested_value[3:]
        try:
            value_1_int = int(value_1_str.lstrip('0'))
            value_2_int = int(value_2_str.lstrip('0'))
        except:
            return None, None
        return value_1_int, value_2_int

    async def on_submit(self, interaction: discord.Interaction):
        # Récupérer les valeurs
        # TextInput: via self.short_1.value
        key_level_str = self.short_1.value
        try:
            key_level_int = int(key_level_str)
        except:
            await interaction.response.send_message(f"ERREUR: La niveau de clé doit être désignée par un nombre", ephemeral=True, delete_after=30)
            return
        if key_level_int >= 31 or key_level_int <= 1:
            await interaction.response.send_message(f"ERREUR: Il faut rentrer un niveau de clé entre 2 et 30", ephemeral=True, delete_after=30)
            return
        
        # Test pour voir si la date est au bon format
        date_str = self.short_2.value
        day_str, month_str = date_str[:2], date_str[3:]
        try:
            day_int = int(day_str.lstrip('0'))
            month_int = int(month_str.lstrip('0'))
            datetime(datetime.now().year, month_int, day_int)
        except:
            await interaction.response.send_message(f"ERREUR: Il faut rentrer des nombres (ex: 10/02 ou 15:00 ou 15h00)", ephemeral=True, delete_after=30)
            return

        # Test pour voir si les heures est minutes sont bien au bon format
        time_str = self.short_3.value
        hour_str, min_str = time_str[:2], time_str[3:]
        if hour_str == "00":
            hour_int = 00
        else:
            try:
                hour_int = int(hour_str.lstrip('0'))
                datetime(datetime.now().year, month_int, day_int, hour_int)
            except:
                await interaction.response.send_message(f"ERREUR: Il faut rentrer des nombres (ex: 10/02 ou 15:00 ou 15h00)", ephemeral=True, delete_after=30)
                return
        if min_str == "00":
            min_int = 00
        else:
            try:
                min_int = int(min_str.lstrip('0'))
                datetime(datetime.now().year, month_int, day_int, hour_int, min_int)
            except:
                await interaction.response.send_message(f"ERREUR: Il faut rentrer des nombres (ex: 10/02 ou 15:00 ou 15h00)", ephemeral=True, delete_after=30)
                return
        
        # Test pour voir si la date est antérieur à maintenant
        try:
            tested_now = datetime(datetime.now().year, month_int, day_int, hour_int, min_int)
        except ValueError as e:
            await interaction.response.send_message(f"ERREUR: La date ou l'heure demandée est invalide: \n Détail:{e}", ephemeral=True, delete_after=30)
            return
        real_now = datetime.now()
        if tested_now < real_now:
            await interaction.response.send_message(f"ERREUR: La date demandée est antérieur à maintenant", ephemeral=True, delete_after=30)
            return

        # Select: discord.py te donne les valeurs via les composants reçus
        # (on parcourt les composants du modal)
        menu_1_value = None
        for item in self.children:
            if isinstance(item, discord.ui.Label) and getattr(item.component, "custom_id", None) == "menu_1":
                tag = ", ".join(element for element in item.component.values)

        # print(item.component.values[1])
        # print(item.component.values[2])

        await interaction.response.send_message(f"Ton event à été créé, n'oublie pas de t'y inscrire !", ephemeral=True, delete_after=30)

        # Requete Raid Helper
        usr = interaction.user.id

        url = f"https://raid-helper.dev/api/v2/servers/{SERVER_ID}/channels/{CHANNEL_ID}/event"
        payload = {
            "leaderId": f"{usr}",
            "templateId": "ct17",
            "title": f"+{key_level_int} Completion",
            "date": f"{int(tested_now.timestamp())}",
            "time": f"{hour_int}:{min_int}",
            "roles": [
                {"name": "Tanks", "limit": 1}, 
                {"name": "Healers", "limit": 1}, 
                {"name": "DPS", "limit": 3}
                ],
            "advancedSettings": {
                "mentions": tag
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{RAID_HELPER_TOKEN}"
        }

        response = requests.post(url, json=payload, headers=headers)

        # await interaction.response.send_message(
        #     f"Reçu ✅\n- menu_1={menu_1_value}\n- short_1={key_level}\n- short_2={date}",
        #     ephemeral=True,
        # )

# Command to trigger the view
@bot.tree.command(name="ticket")
async def ticket_command(interaction: discord.Interaction):
    await interaction.response.send_message("Choose a category:", view=Donjon_Select(), ephemeral=True, delete_after=5)

# Commande pour executer le form
# @bot.tree.command(name="donjon_bis", description="Tester le form donjon")
# async def test(interaction: discord.Interaction):
#    await interaction.response.send_modal(MyForm())

# @bot.event
# async def on_message(message):
#    if message.author.bot:
#       return
#    if message.content == "Bonjour":
#       channel = message.channel
#       await channel.send("Comment tu vas ?")

@bot.tree.command(name="donjon", description="Poster le message pour les donjons")
async def test(interaction: discord.Interaction):
   embed = discord.Embed(
      title="🔑 Organisation des Clés Mythiques+",
      description="""
**Besoin d’un groupe pour une clé ?**
**Utilise le menu déroulant ci-dessous pour indiquer ce que tu cherche 👇**

Deux options s’offrent à toi:

**🎯 Push une clé spécifique**

Tu as UNE clé précise que tu veux monter (ex: Pit +20)
→ Sélectionne cette option si tu cherche à push TA clé.

**📈 Key completion**

Tu veux faire un certain niveau (ex: +12), peu importe le donjon.
→ Sélectionnez cette option si tu es flexible sur l’instance.
""",
      color=discord.Color.blue()
   )
#    embed.add_field(name="Test field", value="Test de value de field") # Ligne pour creer un field dans un embed
   await interaction.response.send_message(embed=embed, view=Donjon_Select())


bot.run(TOKEN) # Démarre le bot (il apparait en ligne)
