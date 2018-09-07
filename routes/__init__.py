import routes.account as account_handlers
import routes.device as device_handlers
import routes.circle as circle_handlers
import routes.circle_logic as circle_logic_handlers
import routes.payment as payment_handlers
import routes.message as message_handlers
import routes.user_message_logic as user_message_handlers
import routes.media as media_handlers
import routes.cookies as cookies_handlers
import routes.media_logic as media_logic_handlers
import routes.device_message_logic as device_message_handlers
import routes.conversation_logic as conversation_logic_handlers
import routes.conversation as conversation_handlers
import routes.facebook as facebook_handlers
import routes.hangout as hangout_handlers


class ResourceManager:
    @staticmethod
    def add_account_resources(api):
        api.add_resource(account_handlers.AccountCreate, '/account/create')
        api.add_resource(account_handlers.AccountLogin, '/account/login')
        api.add_resource(account_handlers.AccountLogout, '/account/logout')
        api.add_resource(account_handlers.AccountModify, '/account/modify')
        api.add_resource(account_handlers.ModifyPassword, '/account/modify/password')
        api.add_resource(account_handlers.PromoteAdmin, '/admin/account/promote')
        api.add_resource(account_handlers.UserInfo, '/user/info')
        api.add_resource(account_handlers.GetUserInfo, '/user/info/<user_id>')
        api.add_resource(account_handlers.MailAvailability, '/email/available')
        api.add_resource(account_handlers.GetMailAvailability, '/email/available/<email>')
        api.add_resource(account_handlers.CheckToken, '/token/verify')

    @staticmethod
    def add_circle_logic_resources(api):
        api.add_resource(circle_logic_handlers.CircleInvite, '/circle/invite')
        api.add_resource(circle_logic_handlers.CircleJoin, '/circle/join')
        api.add_resource(circle_logic_handlers.CircleReject, '/circle/reject')
        api.add_resource(circle_logic_handlers.CircleQuit, '/circle/quit')
        api.add_resource(circle_logic_handlers.CircleKick, '/circle/kick')

    @staticmethod
    def add_circle_resources(api):
        api.add_resource(circle_handlers.CircleCreate, '/circle/create')
        api.add_resource(circle_handlers.CircleUpdate, '/circle/update')
        api.add_resource(circle_handlers.CircleDelete, '/admin/circle/delete')
        api.add_resource(circle_handlers.CircleInfo, '/circle/info')
        api.add_resource(circle_handlers.GetCircleInfo, '/circle/info/<circle_id>')
        api.add_resource(circle_handlers.CircleList, '/circle/list')
        api.add_resource(circle_handlers.GetCircleList, '/user/circle/list')

    @staticmethod
    def add_cookies_resources(api):
        api.add_resource(cookies_handlers.SetCookies, "/cookies/set/token")

    @staticmethod
    def add_conversation_resources(api):
        api.add_resource(conversation_handlers.ConversationCreate, '/admin/conversation/create')
        api.add_resource(conversation_handlers.ConversationDelete, '/admin/conversation/delete')
        api.add_resource(conversation_handlers.ConversationInfo, '/conversation/info')
        api.add_resource(conversation_handlers.GetConversationInfo, '/conversation/info/<conversation_id>')
        api.add_resource(conversation_handlers.ConversationUpdate, '/conversation/update')
        api.add_resource(conversation_handlers.ConversationList, '/conversation/list')
        api.add_resource(conversation_handlers.GetConversationList, '/conversation/list/<circle_id>')

    @staticmethod
    def add_conversation_logic_resources(api):
        api.add_resource(conversation_logic_handlers.ConversationInvite, '/conversation/invite')
        api.add_resource(conversation_logic_handlers.ConversationKick, '/conversation/kick')
        api.add_resource(conversation_logic_handlers.ConversationQuit, '/conversation/quit')
        api.add_resource(conversation_logic_handlers.ConvesationSetDevice, '/conversation/device/set')
        api.add_resource(conversation_logic_handlers.ConversationUserPromote, '/conversation/promote')

    @staticmethod
    def add_message_resources(api):
        api.add_resource(message_handlers.MessageDelete, '/message/delete')
        api.add_resource(message_handlers.MessageInfo, '/message/info')
        api.add_resource(message_handlers.GetMessageInfo, '/message/info/<message_id>')
        api.add_resource(message_handlers.MessageList, '/conversation/message/list')
        api.add_resource(message_handlers.GetMessageList, '/message/list/<conversation_id>/<quantity>')
        api.add_resource(message_handlers.MessageUpdate, '/message/update')

    @staticmethod
    def add_device_message_resources(api):
        api.add_resource(device_message_handlers.FirstDeviceMessageSend, '/device/message/first-message')
        api.add_resource(device_message_handlers.DeviceMessageSend, '/device/message/send')

    @staticmethod
    def add_user_message_resources(api):
        api.add_resource(user_message_logic.FirstMessageSend, '/message/first-message')
        api.add_resource(user_message_logic.MessageSend, '/message/send')
        api.add_resource(user_message_logic.FirstMessageToDeviceSend, '/message/device/first-message')

    @staticmethod
    def add_media_logic_resources(api):
        api.add_resource(media_logic_handlers.FindMedia, "/media/find")
        api.add_resource(media_logic_handlers.CreateMedia, "/media/create")
        api.add_resource(media_logic_handlers.UploadMedia, '/media/upload/<media_id>')
        api.add_resource(media_logic_handlers.MediaRequest, '/media/retrieve')
        api.add_resource(media_logic_handlers.DeleteMedia, '/media/delete')
        api.add_resource(media_logic_handlers.GetMediaRequest, '/media/retrieve/<media_id>')

    @staticmethod
    def add_media_resources(api):
        api.add_resource(media_handlers.MediaDelete, '/admin/media/delete')
        api.add_resource(media_handlers.MediaInfoAdmin, '/admin/media/info')
        api.add_resource(media_handlers.MediaUpdate, '/admin/media/update')
        api.add_resource(media_handlers.MediaInfo, '/media/info')
        api.add_resource(media_handlers.GetMediaInfo, '/media/info/<media_id>')
        api.add_resource(media_handlers.MediaList, '/message/media/list')
        api.add_resource(media_handlers.GetMediaList, '/message/media/list/<message_id>')

    @staticmethod
    def add_api_resources(api):
        api.add_resource(account_handlers.CreateApiToken, '/api/token')
        api.add_resource(facebook_handlers.WebHookMessenger, '/api/messenger/webhook')
        api.add_resource(hangout_handlers.WebHookHangout, '/api/hangout/webhook')

    @staticmethod
    def add_payment_resources(api):
        api.add_resource(payment_handlers.FakePayment, '/device/buy')

    @staticmethod
    def add_device_routes(api):
        api.add_resource(device_handlers.DeviceAdd, '/admin/device/add')
        api.add_resource(device_handlers.DeviceDelete, '/admin/device/delete')
        api.add_resource(device_handlers.DeviceActivate, '/admin/device/activate')
        api.add_resource(device_handlers.DeviceUpdate, '/device/update')
        api.add_resource(device_handlers.DeviceInfo, '/device/info')
        api.add_resource(device_handlers.GetDeviceInfo, '/device/info/<device_id>')
        api.add_resource(device_handlers.DeviceLogin, '/device/authenticate')
        api.add_resource(device_handlers.DeviceCredentials, '/admin/device/credentials')
        api.add_resource(device_handlers.DeviceLogout, '/device/logout')
        api.add_resource(device_handlers.UsernameAvailability, '/device/username/available')
        api.add_resource(device_handlers.GetUsernameAvailability, '/device/username/available/<username>')
        api.add_resource(device_handlers.CheckDeviceToken, '/device/token/verify')
        api.add_resource(device_handlers.ModifyDevicePassword, '/device/modify/password')
