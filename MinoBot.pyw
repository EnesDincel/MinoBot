import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import asyncio
import random
import yt_dlp as ydl
from youtubesearchpython import VideosSearch
import shutil
import os
import youtube_dl

# YouTube'dan ses akışı almayı kolaylaştırmak için ayarlar
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


ydl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,  # Sadece sesi al
    'audioformat': 'mp3',  # Ses formatı
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',  # Çıktı dosya adı
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'source_address': None,  # IP adresi için
}


# Yasaklı kelimelerin seviyelerine göre tanımlanması
low_level_banned_words = ["salak", "gerizekalı"]  # Düşük seviye yasaklı kelimeler
high_level_banned_words = ["piç", "oç" , "domal" , "sik"]  # Yüksek seviye yasaklı kelimeler

# JSON dosyasından kullanıcı verilerini yükleme
def load_user_data():
    try:
        with open("user_data.json", "r") as f:
            # Dosya boşsa "{}" ile doldur
            content = f.read().strip()  # Dosyayı okuyup boşlukları temizler
            if not content:  # Eğer dosya boşsa
                return {}  # Boş bir sözlük döndür
            return json.loads(content)
    except json.JSONDecodeError:
        print("JSON dosyasında bir hata var. Lütfen formatı kontrol edin.")
        return {}  # Hata durumunda boş bir sözlük döndür
    except FileNotFoundError:
        print("JSON dosyası bulunamadı. Yeni bir dosya oluşturuluyor.")
        return {}

# Örnek kullanım
user_data = load_user_data()

# JSON dosyasına kullanıcı verilerini kaydetme
def save_user_data(user_data):
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)

# JSON dosyasından warn verilerini yükleme
def load_warn_data():
    try:
        with open('warn_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# JSON dosyasına warn verilerini kaydetme
def save_warn_data(warn_data):
    with open('warn_data.json', 'w') as f:
        json.dump(warn_data, f)


# Dinamik komutları yükle
def load_dynamic_commands():
    try:
        with open('dynamic_commands.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Dinamik komutları kaydet
def save_dynamic_commands(dynamic_commands):
    with open('dynamic_commands.json', 'w') as f:
        json.dump(dynamic_commands, f)

# Discord botu tanımlama
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot olarak giriş yapıldı: {bot.user.name}')

# Kullanıcı verilerini başlat
user_data = load_user_data()
warn_data = load_warn_data()  # Warn verilerini yükle
dynamic_commands = load_dynamic_commands()  # Dinamik komutları yükle

# Seviyelere göre verilecek rollerin tanımlaması
level_roles = {
    1: 1290331174023069816,  # Seviye 5'te verilecek rolün ID'si (örneğin 'Yeni Üye')
    2: 1290331432891187261, # Seviye 10'da verilecek rolün ID'si (örneğin 'Orta Üye')
    5: 1289659737578672270  # Seviye 20'de verilecek rolün ID'si (örneğin 'Üst Üye')
}


async def on_ready():
    print(f"Bot olarak giriş yapıldı: {bot.user}")

@bot.command()
async def join(ctx):
    """Bot ses kanalına katılır."""
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.send("Önce bir ses kanalına katılmalısın!")
        return
    await channel.connect()
    await ctx.send(f"{channel.name} kanalına katıldım!")

@bot.command(name='play_song')
async def play(ctx, *, song_name):
    """Verilen şarkıyı çalar."""
    voice_client = ctx.voice_client
    if not voice_client:
        await ctx.send("Önce bir ses kanalına katılmalısın!")
        return
    
    # Şarkıyı YouTube'da ara
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegAudioConvertor',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'extractaudio': True,  # Sadece ses
    'outtmpl': 'downloads/%(id)s.%(ext)s',  # İndirilen dosyayı kaydetme
    'audioquality': 1,  # Yüksek ses kalitesi
    'prefer_ffmpeg': True,  # FFmpeg kullanımı
}
"""
    try:
        # yt-dlp kullanarak şarkıyı arama
        with ydl.YoutubeDL(ydl_opts) as ydl_instance:
        try:
            info = ydl_instance.extract_info(f"ytsearch:{song_name}", download=False)
            url = info['entries'][0]['url']
            title = info['entries'][0]['title']
        except Exception as e:
            await ctx.send(f"Şarkı bulunamadı: {e}")

        # Şarkıyı ses kanalında çal
        voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
        await ctx.send(f"Şimdi çalıyor: **{title}**")
    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}")
"""
@bot.command()
async def leave(ctx):
    """Bot ses kanalından ayrılır."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Kanaldan ayrıldım!")
    else:
        await ctx.send("Bot zaten bir ses kanalında değil!")

# Yasaklı kelime kontrolü
async def check_for_banned_words(message):
    content_lower = message.content.lower()
    
    # Düşük seviye yasaklı kelimeleri kontrol et
    for word in low_level_banned_words:
        if word in content_lower:
            await handle_punishment(message, "low")
            return True

    # Yüksek seviye yasaklı kelimeleri kontrol et
    for word in high_level_banned_words:
        if word in content_lower:
            await handle_punishment(message, "high")
            return True

    return False


@bot.command(name='connect')
async def join(ctx):
    """Bot ses kanalına katılır."""
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.send("Önce bir ses kanalına katılmalısın!")
        return
    await channel.connect()
    await ctx.send(f"{channel.name} kanalına katıldım!")


@bot.command()
@commands.has_permissions(manage_messages=True)  # Yalnızca mesaj yönetme izni olanlar kullanabilir
async def sil(ctx, sayi: int):
    """!sil (sayı)"""
    if sayi < 1:
        await ctx.send("Silinecek mesaj sayısı en az 1 olmalıdır.")
        return
    elif sayi > 100:
        await ctx.send("En fazla 100 mesaj silebilirim.")
        return

    deleted = await ctx.channel.purge(limit=sayi)
    await ctx.send(f"{len(deleted)} mesaj silindi.", delete_after=5)  # Mesajı 5 saniye sonra sil

LOG_CHANNEL_ID = 1289648440867029044  # Log kanalının ID'sini buraya yazın

# Banlama işlemi için komut
@bot.command()
@commands.has_permissions(ban_members=True)  # Yalnızca ban yetkisi olanlar kullanabilir
async def ban(ctx, member: discord.Member, *, reason=None):
    """!ban (kişi)"""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} başarıyla banlandı! Sebep: {reason}")
        
        # Log mesajı oluşturma
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"{member} kullanıcısı, {ctx.author} tarafından banlandı. Sebep: {reason}")
    except discord.Forbidden:
        await ctx.send("Bu kullanıcıyı banlamak için yeterli yetkim yok!")
    except discord.HTTPException:
        await ctx.send("Kullanıcıyı banlarken bir hata oluştu.")



# Ban kaldırma işlemi için komut
@bot.command()
@commands.has_permissions(ban_members=True)  # Yalnızca ban yetkisi olanlar kullanabilir
async def unban(ctx, *, member: str):
    """!unban (kişi)"""
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        if (ban_entry.user.name, ban_entry.user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(ban_entry.user)
            await ctx.send(f"{ban_entry.user.mention} banı kaldırıldı.")
            
            # Log mesajı oluşturma
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"{ban_entry.user} kullanıcısının banı, {ctx.author} tarafından kaldırıldı.")
            return

    await ctx.send(f"{member} banlı değil.")

# Log kanalını ayarlamak için bir komut (isteğe bağlı)
@bot.command()
@commands.has_permissions(manage_channels=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    """!set_log_channel (kanal)"""
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id
    await ctx.send(f"Log kanalı olarak {channel.mention} ayarlandı.")

# Ceza işlemleri
async def handle_punishment(message, severity):
    user_id = str(message.author.id)
    
    # Kullanıcı verilerini kontrol et
    if user_id not in warn_data:
        warn_data[user_id] = []
    
    # Ceza türüne göre işlem yap
    if severity == "low":
        warn_data[user_id].append("Düşük seviye yasaklı kelime kullandı.")  # Uyarıyı ekle
        save_warn_data(warn_data)
        await message.channel.send(f"{message.author.mention}, düşük seviye yasaklı kelime kullandığınız için uyarıldınız. Toplam uyarı sayısı: {len(warn_data[user_id])}")
    
        # Uyarı sayısına göre ceza verebiliriz
        if len(warn_data[user_id]) >= 2:
            await mute_user(message.author, 10)  # 10 dakika mute
            await message.channel.send(f"{message.author.mention}, 3 uyarı aldığınız için 10 dakika boyunca sessize alındınız.")
    
    elif severity == "high":
        warn_data[user_id].append("Yüksek seviye yasaklı kelime kullandı.")  # Uyarıyı ekle
        save_warn_data(warn_data)
        await message.channel.send(f"{message.author.mention}, yüksek seviye yasaklı kelime kullandığınız için sessize alındınız.")
        await mute_user(message.author, 30)  # 30 dakika mute
    
    save_warn_data(warn_data)

# Kullanıcıyı belirli süreyle sessize alma (mute)
@bot.command(name='mute')
async def mute(ctx, member: discord.Member, duration_minutes: int):
    """!mute (kişi) (süre dk)"""
    role = discord.utils.get(ctx.guild.roles, name="Muted")  # 'Muted' rolünü alın

    if not role:
        # Eğer 'Muted' rolü yoksa, oluşturalım
        role = await ctx.guild.create_role(name="Muted")

        # Tüm kanallar için 'Muted' rolüne mesaj gönderme iznini kapatalım
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    # Rolü kullanıcıya ver
    await member.add_roles(role)
    await ctx.send(f"{member.mention} için 'Muted' rolü verildi.")

    # Belirli süre boyunca sessizde tut, ardından rolü kaldır
    await asyncio.sleep(duration_minutes * 60)
    await member.remove_roles(role)
    await ctx.send(f"{member.mention} için 'Muted' rolü kaldırıldı.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Botların mesajlarını görmezden gel

    user_id = str(message.author.id)
    
    # Kullanıcının verileri var mı kontrol et, yoksa sıfırla
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}

    # Yasaklı kelime kontrolü
    if await check_for_banned_words(message):
        return

    # Komut kontrolü
    if message.content.startswith('!'):
        command_name = message.content[1:].split()[0]
        
        # Burada dinamik komutlar kontrol edilmiyor, doğrudan mevcut komutları kontrol ediyoruz
        ctx = await bot.get_context(message)
        if command_name in bot.all_commands:
            await bot.invoke(ctx)
            return  # Komut bulundu, burada çıkıyoruz

        # Bilinmeyen komut, kullanıcıdan yanıt iste
        await message.channel.send(f"Bilinmeyen komut: `{command_name}`. Yanıtı kaydetmek ister misin? (e/h)")
        try:
            def check_response(m):
                return m.author == message.author and m.channel == message.channel and m.content.lower() in ['e', 'h']

            response_msg = await bot.wait_for('message', check=check_response, timeout=30)
            
            if response_msg.content.lower() == 'evet':
                await message.channel.send(f"Lütfen `{command_name}` komutu için bir yanıt girin:")
                
                def check_command_response(m):
                    return m.author == message.author and m.channel == message.channel

                command_response = await bot.wait_for('message', check=check_command_response, timeout=30)
                dynamic_commands[command_name] = command_response.content
                save_dynamic_commands(dynamic_commands)
                await message.channel.send(f"`{command_name}` komutu için yanıt kaydedildi.")
            else:
                await message.channel.send("Yanıt kaydedilmedi.")
        except asyncio.TimeoutError:
            await message.channel.send("Zaman aşımına uğradı, yanıt kaydedilmedi.")

    # Verileri kaydet
    save_user_data(user_data)

    # Komutları da işleme
    await bot.process_commands(message)

@bot.command()
async def seviye(ctx, member: discord.Member = None):
    """Kullanıcının seviyesini gösterir."""
    if member is None:
        member = ctx.author  # Eğer üye belirtilmezse, komutu kullanan kişi
    user_id = str(member.id)

    if user_id not in user_data:
        await ctx.send(f"{member.display_name} için kayıt bulunamadı.")
    else:
        level = user_data[user_id]["level"]
        xp = user_data[user_id]["xp"]
        xp_needed = 100 * (level ** 2)

        # Gömülü mesaj oluştur
        embed = discord.Embed(title="Kullanıcı Seviyesi", color=discord.Color.blue())
        embed.add_field(name="Kullanıcı", value=member.display_name, inline=True)
        embed.add_field(name="Seviye", value=level, inline=True)
        embed.add_field(name="XP", value=xp, inline=True)
        embed.add_field(name="Gerekli XP", value=xp_needed - xp, inline=True)

        await ctx.send(embed=embed)

# Kullanıcının mevcut XP'sini sıfırlamak için komut
@bot.command()
@commands.has_permissions(administrator=True)  # Sadece adminler kullanabilir
async def sıfırla(ctx, member: discord.Member):
    """Belirtilen kullanıcının XP ve seviyesini sıfırlar."""
    user_id = str(member.id)

    if user_id in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}
        save_user_data(user_data)
        await ctx.send(f"{member.display_name}'in seviyesi sıfırlandı.")
    else:
        await ctx.send(f"{member.display_name} için veri bulunamadı.")

# Adminlerin kullanıcıya belirli miktarda XP vermesi için komut
@bot.command()
@commands.has_permissions(administrator=True)  # Sadece adminler kullanabilir
async def setxp(ctx, member: discord.Member, amount: int):
    """Belirli bir kullanıcıya XP verir."""
    user_id = str(member.id)

    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}  # Eğer kayıt yoksa sıfırdan başlat
    
    user_data[user_id]["xp"] += amount  # Belirtilen miktarda XP ekle
    save_user_data(user_data)

    await ctx.send(f"{member.display_name}'e {amount} XP verildi. Şu anki XP'si: {user_data[user_id]['xp']}")

# İlk 10 kullanıcının XP sıralamasını gösteren komut
@bot.command()
async def sıralama(ctx):
    """Sunucudaki en yüksek XP'ye sahip ilk 10 kullanıcıyı sıralar."""
    # Kullanıcıları XP'ye göre sırala ve ilk 10 kişiyi al
    sorted_users = sorted(user_data.items(), key=lambda item: item[1]["xp"], reverse=True)
    top_10 = sorted_users[:10]  # İlk 10 kişiyi seç

    if len(top_10) == 0:
        await ctx.send("Henüz kimse XP kazanmamış.")
        return

    # Gömülü mesaj oluştur
    embed = discord.Embed(title="**XP Sıralaması (İlk 10 Kullanıcı):**", color=discord.Color.blue())

    for i, (user_id, data) in enumerate(top_10, 1):
        user = await bot.fetch_user(int(user_id))  # Kullanıcının adını almak için ID'yi kullan
        embed.add_field(name=f"{i}. {user.display_name}", value=f"{data['xp']} XP (Seviye {data['level']})", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)  # Warn komutunu sadece mesaj yönetme izni olanlar kullanabilir
async def warn(ctx, member: discord.Member, *, reason=None):
    """!warn (kişi)"""
    user_id = str(member.id)

    if user_id not in warn_data:
        warn_data[user_id] = []  # Kullanıcının warn verilerini başlat

    warn_data[user_id].append(reason or "Sebep belirtilmedi")  # Uyarıyı kaydet
    save_warn_data(warn_data)

    # Gömülü mesaj oluştur
    embed = discord.Embed(title="Uyarı Verildi", color=discord.Color.orange())
    embed.add_field(name="Kullanıcı", value=member.display_name, inline=True)
    embed.add_field(name="Sebep", value=reason or "Sebep belirtilmedi", inline=True)
    embed.add_field(name="Toplam Uyarı Sayısı", value=len(warn_data[user_id]), inline=True)

    await ctx.send(embed=embed)

# Warnları gösteren komut
@bot.command()
async def uyarılar(ctx, member: discord.Member = None):
    """!uyarılar (kişi)"""
    if member is None:
        member = ctx.author  # Eğer üye belirtilmezse, komutu kullanan kişi
    user_id = str(member.id)

    if user_id not in warn_data or len(warn_data[user_id]) == 0:
        await ctx.send(f"{member.display_name} için herhangi bir uyarı bulunamadı.")
    else:
        warn_list = "\n".join([f"{i+1}. {reason}" for i, reason in enumerate(warn_data[user_id])])
        await ctx.send(f"{member.display_name}'in uyarıları:\n{warn_list}")

from discord.utils import get

TICKET_CATEGORY_ID = 1312715413909671979  # Ticket'ların açılacağı kategori ID'si
MODERATOR_ROLE_ID = 1315283866331643904  # Moderatörlerin rol ID'si

class TicketView(View):
    @discord.ui.button(label="Ticket Aç", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        if interaction.guild is None:
            await interaction.response.send_message("Bu komut sadece bir sunucuda kullanılabilir.", ephemeral=True)
            return
        
        category = bot.get_channel(TICKET_CATEGORY_ID)
        existing_channel = discord.utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")

        if existing_channel:
            embed = discord.Embed(
                title="Hata",
                description=f"{interaction.user.mention}, zaten açık bir ticket'iniz var: {existing_channel.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(MODERATOR_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            ticket_channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name.lower()}", category=category, overwrites=overwrites)
            
            embed = discord.Embed(
                title="Ticket Oluşturuldu",
                description=f"{interaction.user.mention}, ticket'iniz oluşturuldu. Moderatörler yakında sizinle iletişime geçecek.",
                color=discord.Color.green()
            )
            await ticket_channel.send(embed=embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Ticket Kapat", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        if interaction.channel is None or not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("Bu komutu sadece bir ticket kanalında kullanabilirsiniz.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Ticket Kapatılıyor",
            description=f"{interaction.user.mention}, ticket kapatılıyor...",
            color=discord.Color.yellow()
        )
        await interaction.channel.send(embed=embed)
        await asyncio.sleep(3)
        await interaction.channel.delete()

@bot.command()
async def ticket(ctx):
    view = TicketView()
    embed = discord.Embed(
        title="Ticket Sistemi",
        description="Ticket açmak veya kapatmak için aşağıdaki butonlara tıklayın:",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view)



# Bot'un token'ını buraya ekleyin
bot.run('MTI5MDMwOTQ2MTEzODczOTMwMA.GNTgfA.09ZG0Aahde3YjliXWvuo3laqFuCDBalsT0cfFc')  # Token'ınızı buraya eklemeyi unutmayın
