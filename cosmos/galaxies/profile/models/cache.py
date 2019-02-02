from .user_profile import CosmosUserProfile


class ProfileCache(object):

    def __init__(self, plugin):
        self.plugin = plugin
        self.bot = self.plugin.bot
        self._redis = None
        self.__collection_name = self.plugin.data.profile.collection_name
        self.collection = self.bot.db[self.__collection_name]

    async def prepare(self):
        self.bot.log.info("Preparing profile caches.")
        await self.bot.wait_until_ready()
        self._redis = self.bot.cache.redis
        profile_documents = dict()
        profiles_data = await self.collection.find({}).to_list(None)
        for profile_document in profiles_data:
            profile = CosmosUserProfile.from_document(profile_document)
            user_id = int(profile_document.get("user_id"))  # bson.int64.Int64 to int
            profile_documents[user_id] = profile
        await self._redis.set_objects(self.__collection_name, profile_documents)
        profile_count = await self._redis.hlen(self.__collection_name)
        self.bot.log.info(f"Loaded {profile_count} profiles to cache.")

    async def get_profile(self, user_id: int) -> CosmosUserProfile:
        profile = await self._redis.get_object(self.__collection_name, user_id)
        if not profile:
            profile_document = await self.collection.find_one({"user_id": user_id})
            if profile_document:
                profile = CosmosUserProfile.from_document(profile_document)
                await self._redis.set_object(self.__collection_name, user_id, profile)
        return profile

    async def create_profile(self, user_id: int) -> CosmosUserProfile:
        profile_document = self.plugin.data.profile.document_schema
        profile_document.update({"user_id": user_id})
        await self.collection.insert_one(profile_document)
        return await self.get_profile(user_id)

    async def get_profile_embed(self, ctx):
        profile = await self.get_profile(ctx.author.id)
        if not profile:
            async with ctx.loading():
                await ctx.send(embed=self.bot.theme.embeds.one_line.primary("Welcome. Creating your Cosmos profile!"))
                profile = await self.create_profile(ctx.author.id)
        embed = self.bot.theme.embeds.primary(title="Profile")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Reputation points", value=str(profile.reps))
        embed.add_field(name="Level", value=str(profile.level))
        embed.add_field(name="Experience points", value=str(profile.xp))
        description = profile.description or self.plugin.data.profile.default_description
        embed.add_field(name="Profile description", value=description)
        return embed
