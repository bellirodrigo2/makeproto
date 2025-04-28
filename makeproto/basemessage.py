
from dataclasses import dataclass

from makeproto.basefield import Int32, String


class BaseMessage:
    proto_file: str

@dataclass
class User(BaseMessage):
    proto_file = "file.proto"  # apenas atributo da classe

    id: Int32
    name: String
    email:String
    tags:list[String]




# message User {
#     int32 id = 1;
#     string name = 2;
#     string email = 3;
#     repeated string tags = 4;
# }

# message Product {
#     string name = 1;
#     string type = 2;
#     float unit_price = 3;
# }

# message Requisition {
#     User user = 1;
#     Product product = 2;
#     int32 quantity = 3;
# }

# message ReqResponse{
#     string msg = 1;
#     float total_value=2;
# }