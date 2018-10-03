from Facebook.models import FBPage
from .commonThread import *


class FbPageUpdater(CommonThread):
    batchSize = 1  # number of pages requested at once
    fieldsPerChunk = 100  # number of fields requested in each API call
    workQueueName = 'pageUpdateQueue'
    allFields = [
        'id',
        'about',
        #'access_token',
        #'ad_campaign',
        #'affiliation',
        #'app_id',
        #'app_links',
        #'artists_we_like',
        #'attire',
        #'awards',
        #'band_interests',
        #'band_members',
        #'best_page',
        #'bio',
        #'birthday',
        #'booking_agent',
        #'built',
        #'business',
        #'can_checkin',
        #'can_post',
        #'category',
        #'category_list',
        #'checkins',
        #'company_overview',
        #'connected_instagram_account',
        #'contact_address',
        #'context',
        #'copyright_attribution_insights',
        #'copyright_whitelisted_ig_partners',
        #'country_page_likes',
        #'cover',
        #'culinary_team',
        #'current_location',
        'description',
        #'description_html',
        #'directed_by',
        #'display_subtext',
        #'displayed_message_response_time',
        'emails',
        #'engagement',
        'fan_count',
        #'featured_video',
        #'features',
        #'food_styles',
        #'founded',
        'general_info',
        'general_manager',
        'genre',
        #'global_brand_page_name',
        #'global_brand_root_id',
        #'has_added_app',
        #'has_whatsapp_number',
        #'hometown',
        #'hours',
        #'impressum',
        #'influences',
        #'instagram_business_account',
        #'instant_articles_review_status',
        #'is_always_open',
        #'is_chain',
        'is_community_page',
        #'is_eligible_for_branded_content',
        #'is_messenger_bot_get_started_enabled',
        #'is_messenger_platform_bot',
        'is_owned',
        #'is_permanently_closed',
        #'is_published',
        #'is_unclaimed',
        #'is_webhooks_subscribed',
        #'leadgen_form_preview_details',
        #'leadgen_has_crm_integration',
        #'leadgen_has_fat_ping_crm_integration',
        #'leadgen_tos_acceptance_time',
        #'leadgen_tos_accepted',
        #'leadgen_tos_accepting_user',
        'link',
        'location',
        #'members',
        #'merchant_id',
        #'merchant_review_status',
        #'messenger_ads_default_icebreakers',
        #'messenger_ads_default_page_welcome_message',
        #'messenger_ads_default_quick_replies',
        #'messenger_ads_quick_replies_type',
        'mission',
        #'mpg',
        'name',
        #'name_with_location_descriptor',
        #'network',
        #'new_like_count',
        #'offer_eligible',
        #'overall_star_rating',
        #'page_token',
        #'parent_page',
        #'parking',
        #'payment_options',
        #'personal_info',
        #'personal_interests',
        #'pharma_safety_info',
        #'phone',
        #'place_type',
        #'plot_outline',
        #'preferred_audience',
        #'press_contact',
        #'price_range',
        #'produced_by',
        #'products',
        #'promotion_eligible',
        #'promotion_ineligible_reason',
        #'public_transit',
        #'publisher_space',
        'rating_count',
        #'recipient',
        #'record_label',
        #'release_date',
        #'restaurant_services',
        #'restaurant_specialties',
        #'schedule',
        #'screenplay_by',
        #'season',
        #'single_line_address',
        #'starring',
        #'start_info',
        #'store_code',
        #'store_location_descriptor',
        #'store_number',
        #'studio',
        #'supports_instant_articles',
        'talking_about_count',
        #'unread_message_count',
        #'unread_notif_count',
        #'unseen_message_count',
        'username',
        #'verification_status',
        #'voip_info',
        'website',
        'were_here_count',
        #'whatsapp_number',
        #'written_by',
    ]

    # @facebookLogger.debug(showArgs=True)
    def method(self, fbPageList):

        response = self.gatherInfos(fbPageList)

        for ident in response.keys():
            if threadsExitFlag[0]: return
            fbPage = FBPage.objects.get(_ident=ident)
            fbPage.update(response[ident])
        for fbPage in fbPageList:
            if fbPage._ident not in response.keys():
                log("%s was not retrievable from facebook" % fbPage)
                fbPage.error_on_update = True
                fbPage.save()

    def gatherInfos(self, fbPageList):
        responses = []
        client = getClient()
        for fieldList in [self.allFields[x:x + self.fieldsPerChunk] for x in range(
                0, len(self.allFields), self.fieldsPerChunk)]:
            try:
                responses.append(client.get("",
                                            ids=",".join([page._ident for page in fbPageList]), fields=fieldList))
            except:
                logError('Facebook API rejected fields %s' % fieldList)
        returnClient(client)
        return mergeDicts(responses)


def mergeDicts(dictList):
    result = {}
    for d in dictList:
        for key, value in d.items():
            if not key in result: result[key] = {}
            for subKey, subValue in value.items():
                result[key][subKey] = subValue
    return result
