from dataclasses import dataclass

from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.base_client import PurelymailAPI
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.requests import (
	CreateAppPasswordRequest,
	CreateUserRequest,
	DeleteAppPasswordRequest,
	DeletePasswordResetRequest,
	DeleteUserRequest,
	EmptyRequest,
	GetUserRequest,
	ListPasswordResetRequest,
	ModifyUserRequest,
	UpsertPasswordResetRequest,
)
from ansible_collections.bofzilla.purelymail.plugins.module_utils.clients.types.responses import (
	CreateAppPasswordResponse,
	EmptyResponse,
	GetUserResponse,
	ListPasswordResetResponse,
	ListUsersResponse,
)


@dataclass()
class UserClient:
	api: PurelymailAPI

	def create_user(self, req: CreateUserRequest) -> EmptyResponse:
		return self.api.post("/createUser", req, EmptyResponse)

	def delete_user(self, req: DeleteUserRequest) -> EmptyResponse:
		return self.api.post("/deleteUser", req, EmptyResponse)

	def list_users(self, req: EmptyRequest = EmptyRequest()) -> ListUsersResponse:  # noqa: B008
		return self.api.post("/listUser", req, ListUsersResponse)

	def modify_user(self, req: ModifyUserRequest) -> EmptyResponse:
		return self.api.post("/modifyUser", req, EmptyResponse)

	def get_user(self, req: GetUserRequest) -> GetUserResponse:
		return self.api.post("/getUser", req, GetUserResponse)

	def upsert_password_reset(self, req: UpsertPasswordResetRequest) -> EmptyResponse:
		return self.api.post("/upsertPasswordReset", req, EmptyResponse)

	def delete_password_reset(self, req: DeletePasswordResetRequest) -> EmptyResponse:
		return self.api.post("/deletePasswordReset", req, EmptyResponse)

	def list_password_reset(self, req: ListPasswordResetRequest) -> ListPasswordResetResponse:
		return self.api.post("/listPasswordReset", req, ListPasswordResetResponse)

	def create_app_password(self, req: CreateAppPasswordRequest) -> CreateAppPasswordResponse:
		return self.api.post("/createAppPassword", req, CreateAppPasswordResponse)

	def delete_app_password(self, req: DeleteAppPasswordRequest) -> EmptyResponse:
		return self.api.post("/deleteAppPassword", req, EmptyResponse)
