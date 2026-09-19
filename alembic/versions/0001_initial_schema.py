from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    sport_type_enum = postgresql.ENUM(
        "netball", "cricket", "tennis", "badminton", "futsal", "other",
        name="sporttype",
    )
    booking_status_enum = postgresql.ENUM(
        "pending", "confirmed", "cancelled", name="bookingstatus"
    )
    payment_status_enum = postgresql.ENUM(
        "pending", "success", "failed", name="paymentstatus"
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("phone", sa.String, nullable=False, unique=True),
        sa.Column("email", sa.String, nullable=True, unique=True),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("is_owner", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "courts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("sport_type", sport_type_enum, nullable=False),
        sa.Column("rate_per_hour", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("court_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courts.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", booking_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT no_overlapping_bookings
        EXCLUDE USING gist (
            court_id WITH =,
            tstzrange(start_time, end_time) WITH &&
        ) WHERE (status != 'cancelled')
        """
    )

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payhere_order_id", sa.String, nullable=False, unique=True),
        sa.Column("payhere_payment_id", sa.String, nullable=True),
        sa.Column("status", payment_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.execute("ALTER TABLE bookings DROP CONSTRAINT no_overlapping_bookings")
    op.drop_table("bookings")
    op.drop_table("courts")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS bookingstatus")
    op.execute("DROP TYPE IF EXISTS sporttype")