from dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import DeleteUserRequest, EmptyRequest, GetUserRequest
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import EmptyResponse, GetUserResponse, ListUsersResponse


@dataclass()
class UserClient:
	api: PurelymailAPI

	# def create_user(self, req: CreateUserRequest) -> EmptyResponse:
	# 	return self.api.post("/api/v0/createUser", req, EmptyResponse)

	def delete_user(self, req: DeleteUserRequest) -> EmptyResponse:
		return self.api.post("/api/v0/deleteUser", req, EmptyResponse)

	def list_users(self, req: EmptyRequest = EmptyRequest()) -> ListUsersResponse:  # noqa: B008
		return self.api.post("/api/v0/listUser", req, ListUsersResponse)

	# def modify_user(self, req: ModifyUserRequest) -> EmptyResponse:
	# 	return self.api.post("/api/v0/modifyUser", req, EmptyResponse)

	def get_user(self, req: GetUserRequest) -> GetUserResponse:
		return self.api.post("/api/v0/getUser", req, GetUserResponse)

	# def upsert_password_reset(self, req: UpsertPasswordResetRequest) -> EmptyResponse:
	# 	return self.api.post("/api/v0/upsertPasswordReset", req, EmptyResponse)

	# def delete_password_reset(self, req: DeletePasswordResetRequest) -> EmptyResponse:
	# 	return self.api.post("/api/v0/deletePasswordReset", req, EmptyResponse)

	# def list_password_reset(self, req: ListPasswordResetRequest) -> ListPasswordResetResponse:
	# 	return self.api.post("/api/v0/listPasswordReset", req, ListPasswordResetResponse)

	# def create_app_password(self, req: CreateAppPasswordRequest) -> CreateAppPasswordResponse:
	# 	return self.api.post("/api/v0/createAppPassword", req, CreateAppPasswordResponse)

	# def delete_app_password(self, req: DeleteAppPasswordRequest) -> EmptyResponse:
	# 	return self.api.post("/api/v0/deleteAppPassword", req, EmptyResponse)
