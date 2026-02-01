## 2026-02-01

## Project Update: Enhanced Supabase RLS Management & New List Functionality

This update introduces significant architectural changes to how we interact with Supabase, focusing on robust Row Level Security (RLS) management, alongside new features for board list management and improved data integrity.

### Key Architectural & Core Utility Changes

1.  **Supabase Client Separation (`functions/supabase_client.py`):**
    *   **Change:** The single `supabase` client instance has been split into two distinct clients:
        *   `supabase_client`: Uses the `SUPABASE_ANON_KEY` for regular user-authenticated requests, which will respect Supabase's Row Level Security (RLS) policies.
        *   `supabase_admin`: Uses the `SUPABASE_SERVICE_ROLE_KEY` for server-side administrative operations, allowing the backend to bypass RLS when necessary (e.g., for creating users, or managing data that the current authenticated user might not have direct RLS permissions for).
    *   **Intent/Direction:** This is a crucial security and architectural enhancement. It ensures that user-initiated actions are always governed by RLS, while backend processes (which often require elevated privileges) can operate without RLS constraints. This clarifies the security context of every Supabase interaction.

2.  **Flexible Database Actions (`functions/db_actions.py`):**
    *   **Change:** The `DBActions` class now accepts an optional `use_admin` flag in its constructor (`DBActions(use_admin=True)`).
        *   If `use_admin` is `True`, it will instantiate with the `supabase_admin` client (bypassing RLS).
        *   Otherwise (default `False`), it uses the `supabase_client` (respecting RLS).
    *   **New Function:** Introduced a new `batch_update(table: str, updates: list)` method for performing multiple record updates in a single call, improving efficiency for related data changes.
    *   **Intent/Direction:** Centralizes the logic for choosing the appropriate Supabase client (RLS-enabled vs. RLS-bypassing). This makes it explicit and easier to manage which operations require administrative privileges. The `batch_update` enables more efficient bulk operations, particularly useful for features like list reordering.

### Boards Module Enhancements

1.  **Board Slug Uniqueness (`boards/serializers.py`):**
    *   **Modified Function:** `BoardSerializer.save()`
    *   **New Function:** `BoardSerializer.get_unique_slug(db, base_slug, board_id=None)`
    *   **Change:** When creating or updating a board, the slug is now automatically generated to be unique. If the generated slug (from the board's name) already exists, a counter will be appended (e.g., `my-board`, `my-board-1`, `my-board-2`).
    *   **Intent/Direction:** Improves data integrity and provides more user-friendly, consistent URLs for boards by ensuring each board has a distinct slug.

2.  **Automatic List Repositioning (`boards/serializers.py`):**
    *   **Modified Function:** `ListSerializer.save()`
    *   **New Function:** `ListSerializer._reposition_lists(db, board_id, old_position, new_position)`
    *   **Change:** When a list's `position` is updated, the `ListSerializer` now automatically adjusts the positions of other lists within the same board to maintain a continuous ordering. This uses the new `DBActions().batch_update` for efficiency.
    *   **Intent/Direction:** Enhances the user experience by automating the tedious task of manually adjusting positions when reordering lists, making list management smoother and more intuitive.

3.  **Refactored Board Data Retrieval (`boards/views.py` & `boards/helpers/board_helpers.py`):**
    *   **New File (Untracked in diff, but imported):** `boards/helpers/board_helpers.py`
    *   **Change:** The `GetBoardsView` now delegates fetching board data to `get_full_boards_data` from the new `board_helpers.py`. This helper likely encapsulates more complex queries to fetch comprehensive board information (e.g., boards with their associated lists and cards).
    *   **Intent/Direction:** Improves modularity and keeps views cleaner by moving complex data aggregation logic into dedicated helper functions, paving the way for richer board data fetching.

4.  **New List Creation Endpoint (`boards/views.py` & `boards/urls.py`):**
    *   **New Class:** `boards.views.CreateListView`
    *   **New Endpoint:** `/boards/add-list/`
    *   **Change:** A new API endpoint and view have been added to allow the creation of lists within boards. This view leverages the `ListSerializer` which includes the new automatic repositioning logic.
    *   **Intent/Direction:** Introduces core functionality for managing lists within boards, a fundamental component of the project's task management system.

5.  **Consistent `DBActions` Admin Usage in `boards/views.py`:**
    *   **Change:** All `DBActions` calls within `CreateBoardView`, `GetBoardInfoView`, `UpdateBoardView`, and `DeleteBoardView` now explicitly use `DBActions(use_admin=True)`. Similarly, serializers for creation pass `client=supabase_admin`.
    *   **Intent/Direction:** Ensures that backend operations related to board and list management consistently leverage the RLS-bypassing admin client where appropriate, preventing RLS errors for backend-driven data modifications.

### Core Module Adjustments

1.  **New Image Endpoint (`core/urls.py`):**
    *   **New Endpoint:** `/get-images/`
    *   **Change:** A new URL path has been added, pointing to `views.GetImagesView`.
    *   **Intent/Direction:** Introduces an API endpoint for retrieving images, likely for board backgrounds, user profiles, or other visual assets.

2.  **Supabase Client Consistency in `core/views.py`:**
    *   **Change:** All Supabase client interactions across user authentication (sign-up, login, logout, refresh, Google OAuth) now explicitly use `supabase_client`. Database operations for `users`, `waitlist`, and admin user creation via `supabase_admin.auth.admin.create_user` now use `DBActions(use_admin=True)` or `supabase_admin`.
    *   **Intent/Direction:** Applies the new Supabase client separation consistently across the core user management and authentication flows, ensuring RLS is respected for user-facing actions and bypassed for necessary backend administrative tasks.

---

This comprehensive update strengthens the project's foundation by implementing robust security practices with Supabase RLS and introduces crucial new features for managing board lists with an improved user experience.

## 2026-01-23

### Project Update Summary

This update focuses on two key areas: enhancing the `boards` module with new functionality for deleting boards, and improving the robustness of the Google authentication callback process in the `core` module by adding comprehensive error handling.

---

### **1. `boards/views.py` Changes: Board Deletion Endpoint**

**Intent:** To introduce the capability for users to delete their own boards via a new API endpoint.

**Key Changes & Functionality:**

*   **New API Endpoint for Board Deletion:**
    *   A new class `DeleteBoardView(APIView)` has been added.
    *   It exposes a `DELETE` HTTP method handler: `def delete(self, request, board_id: str)`.
*   **Authentication & Authorization:**
    *   Uses `getTokenFromMiddleware(request)` to extract the `user_id` from the request token.
    *   Includes a check `if not user_id: raise AuthenticationFailed(...)` to ensure the token contains valid user information.
    *   **Crucially**, it implements authorization logic: `if i['creator_id'] != user_id: return Response({"message": "You are not authorized to delete this board"}, status=status.HTTP_401_UNAUTHORIZED)`. This ensures that only the original creator of a board can delete it.
*   **Database Interactions:**
    *   Retrieves the board using `DBActions().get('boards', board_id)`.
    *   Handles cases where the board is not found: `if not board.data: return Response({"message": "Board not found"}, ...)`.
    *   Performs the deletion using `DBActions().delete('boards', board_id)`.
*   **Error Handling:**
    *   The entire deletion logic is wrapped in a `try...except Exception as e:` block.
    *   Logs errors using `logger.error(f"Failed to delete board: {e}")` and returns a `HTTP_400_BAD_REQUEST` for general failures.
*   **Permissions:** Set to `permission_classes = [AllowAny]` which implies authentication will be handled internally by `getTokenFromMiddleware` and authorization by the `creator_id` check.

---

### **2. `core/views.py` Changes: Enhanced Google Callback Error Handling**

**Intent:** To make the `GoogleCallback` authentication process more robust by catching and handling potential errors gracefully, preventing unhandled exceptions during user login or creation via Google SSO.

**Key Changes & Functionality:**

*   **Comprehensive Error Wrapping:**
    *   The entire existing logic within the `GoogleCallback` class's `post` method, responsible for checking existing users, creating new users, and logging them in via Supabase with Google ID tokens, has been wrapped in a `try...except Exception as e:` block.
*   **Centralized Error Response:**
    *   Instead of potentially failing silently or with specific, localized error returns, any exception occurring within the Google login/signup flow will now be caught.
    *   The error is printed to the console (`print(f"Error during Google login: {e}")`) for server-side debugging.
    *   A generic `JsonResponse({"error": str(e)}, status=500)` is returned, providing a consistent 500 status and the error message to the client.
*   **Impact:** This change significantly improves the stability of the Google SSO integration by preventing server crashes due to unexpected issues during the authentication process and providing clearer feedback in case of failures.

